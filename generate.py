from cmsis_svd.parser import SVDParser
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


ints = enumerate_interrupts(device)
env = Environment(loader=FileSystemLoader("templates"))
vectors_template = env.get_template("vectors.c.j2")
device_template = env.get_template("device.h.j2")
open("vectors.c", "w").write(vectors_template.render(interrupts=ints))
open("device.h", "w").write(device_template.render(interrupts=ints,
peripherals=device.peripherals))

for p in device.peripherals:
  if p.registers:
    print(p.registers[0].fields[0].__dict__)
