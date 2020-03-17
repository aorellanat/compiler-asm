import re
import data
from numpy import binary_repr

source_file = open("source.asm", "r")
program_file = open("program.bin", "w+")

def get_operands_number(opcode):
  return data.opcode_operands_number[opcode]

def remove_empty(lines):
  return [line for line in lines if line != ""]

def process_instruction(instruction):
  return remove_empty(re.split('[" " ,]', instruction))

def is_label(instruction):
  return re.match("\w+:$", instruction)

def get_opcode(operation):
  return data.opcode_binary[operation]

def is_direct_register(operand):
  return re.match('^R([0-5]|A|B)$', operand)

def is_indirect_register(operand):
  return re.match('^\$R([0-5]|A|B)$', operand)

def is_memory(operand):
  return re.match('^\$((2[0-5][0-5])|([0-1]?[0-9]?[0-9]))$', operand)

def is_constant(operand):
  return re.match('^((2[0-5][0-5])|([0-1]?[0-9]?[0-9]))$', operand)

def define_type(operand):
  type_matched = is_direct_register(operand)
  if type_matched:
    return 'rd'
  else:
    type_matched = is_indirect_register(operand)
    if type_matched:
      return 'ri'
    else:
      type_matched = is_memory(operand)
      if type_matched:
        return 'm'
      else:
        type_matched = is_constant(operand)
        if type_matched:
          return 'c'
        else:
          return '-'

def select_operands_addressing(operand1, operand2):
  
  addressing = (operand1 + ',' + operand2) if operand2 != "" else operand1

  switcher = {
                "m": "000",
                "rd": "001",
                "c": "010",
                "rd,rd":'000',
                "rd,m":'001',
                "rd,c":'010',
                "rd,ri":'011',
                "ri,rd":'100',
                "ri,c":'101',
                "m,c":'110',
                "m,rd": '111'
             }

  return switcher.get(addressing, "Invalid addressing")

def get_binary8(number):
  return "11111111" if number < 0 or number > 255 else binary_repr(number, width=8)

def get_register_binary(register):
  if register == 'A':
    return get_binary8(6)
  elif register == 'B':
    return get_binary8(7)
  else:
    return get_binary8(int(register))

def get_operand(operand_type, operand_value):
  if operand_type == 'rd':
    operand_value = operand_value.replace('R', '')
    return get_register_binary(operand_value)
  elif operand_type == 'ri':
    operand_value = operand_value.replace('$R', '')
    return get_register_binary(operand_value)
  else:
    return get_binary8(int(operand_value))

def main():
  source_asm =  source_file.read()
  lines = remove_empty(source_asm.split("\n"))

  for line in lines:
    instruction_processed = process_instruction(line)
    print("Instruccion:")
    print(instruction_processed)

    if is_label(instruction_processed[0]) and len(instruction_processed) == 1:
      instruction_processed[0] = instruction_processed[0].replace(':', '')
      data.labels[instruction_processed[0]] = "0000"
    else:
      operands_number = int(get_operands_number(instruction_processed[0]))
      instruction_processed[0] = get_opcode(instruction_processed[0])
      operands = []

      if operands_number == 2:
        operands.append(define_type(instruction_processed[1]))
        operands.append(define_type(instruction_processed[2]))

        instruction_processed[0] += select_operands_addressing(operands[0], operands[1])

      else:
        operands.append(define_type(instruction_processed[1]))
        instruction_processed[0] += select_operands_addressing(operands[0], '')

      for i in range(len(operands)):
        instruction_processed[0] += get_operand(operands[i], instruction_processed[i + 1])

    program_file.write(instruction_processed[0] + "\n")

main()
