from cmsis_svd.parser import SVDParser, SVDRegister, SVDField, SVDPeripheral
from jinja2 import Environment, FileSystemLoader
import json
import sys

parser = SVDParser.for_xml_file(sys.argv[1])
device = parser.get_device()

def enumerate_interrupts(device):
  interrupts = set()
  for p in device.peripherals:
    if not p.interrupts:
      continue
    for i in p.interrupts:
      interrupts.add(i)

  interrupts = list(interrupts)
  interrupts.sort(key=lambda x: x.value)
  return interrupts

class Field:
  def __init__(self, field: SVDField):
    self.name = field.name
    self.description = field.description
    self.bit_width = field.bit_width
    self.bit_offset = field.bit_offset

class ReservedSpace:
  def __init__(self, position, size):
    self.size = size
    self.address_offset = position
    self.name = f"RESERVED_{position}"
    self.modifier = "volatile const"

class Register:
  def __init__(self, register: SVDRegister):
    self.name = register.name
    self.size = 1
    self.description = register.description
    self.address_offset = register.address_offset
    self.fields = [Field(f) for f in register.fields]
    self.access = register.access
    if self.access == "read-only":
      self.modifier = "volatile const"
    else:
      self.modifier = "volatile"

class Peripheral:
   def __init__(self, periph: SVDPeripheral):
     self.name = periph.name
     self.base_address = periph.base_address
     self.group = periph.group_name
     self.generate_defines = True if periph.derived_from is None else False
     self.locations = {}
     for register in periph.registers:
       reg = Register(register)
       if reg.address_offset not in self.locations.keys():
         self.locations[reg.address_offset] = []
       self.locations[reg.address_offset].append(reg)

     end_of_last = 0
     for addr in sorted(self.locations.keys()):
       delta = addr - end_of_last
       if delta > 0:
         self.locations[end_of_last] = [ReservedSpace(end_of_last, delta / 4)]
       end_of_last = addr + 4


ints = enumerate_interrupts(device)
periphs = [Peripheral(p) for p in device.peripherals]
env = Environment(loader=FileSystemLoader("templates"))
vectors_template = env.get_template("vectors.c.j2")
device_template = env.get_template("device.h.j2")
validate_template = env.get_template("validate.c.j2")
open("vectors.c", "w").write(vectors_template.render(interrupts=ints))
open("device.h", "w").write(device_template.render(interrupts=ints, peripherals=periphs))
open("validate.c", "w").write(validate_template.render(peripherals=device.peripherals))
