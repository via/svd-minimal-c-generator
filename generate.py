from cmsis_svd.parser import SVDParser, SVDRegister, SVDField
from jinja2 import Environment, FileSystemLoader




parser = SVDParser.for_xml_file('STM32H743.svd')
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
    self.access = field.access

class Register:
  def __init__(self, register: SVDRegister):
    self.name = register.name
    self.description = register.description
    self.address_offset = register.address_offset
    self.fields = [Field(f) for f in register.fields]



ints = enumerate_interrupts(device)
env = Environment(loader=FileSystemLoader("templates"))
vectors_template = env.get_template("vectors.c.j2")
device_template = env.get_template("device.h.j2")
open("vectors.c", "w").write(vectors_template.render(interrupts=ints))
open("device.h", "w").write(device_template.render(interrupts=ints,
peripherals=device.peripherals))

#for p in device.peripherals:
#  r = Register(p.registers[0])
#  print(r.__dict__)
