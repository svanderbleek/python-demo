import struct
import itertools
import dataclasses

HEADER = 5

DEBIT = 0
CREDIT = 1
START = 2
END = 3

USER = 2456938384156277127

@dataclasses.dataclass
class Result:
  debits: float = 0.0
  credits: float = 0.0
  started: int = 0
  ended: int = 0
  balance: float = 0.0

def read_uint32(io):
  return struct.unpack("!I", io.read(4))[0]

def read_uint64(io):
  return struct.unpack("!Q", io.read(8))[0]

def read_float64(io):
  return struct.unpack("!d", io.read(8))[0]

def read_enum(io):
  return struct.unpack("!B", io.read(1))[0]

def process_log():
  with open("txnlog.dat", "rb") as log:
    log.seek(HEADER)
    records = read_uint32(log)
    result = Result()

    for _ in itertools.repeat(None, records):
      type = read_enum(log)
      time = read_uint32(log)
      user = read_uint64(log)

      if type in [DEBIT, CREDIT]:
        amount = read_float64(log)
        if type == DEBIT:
          result.debits += amount
          if user == USER:
            result.balance -= amount
        else:
          result.credits += amount
          if user == USER:
            result.balance += amount
      elif type == START:
        result.started += 1
      elif type == END:
        result.ended += 1
      else:
        raise ValueError(f"Unknown record type {type}")

  return result

def display(result):
  print(f"total credit amount={result.credits}")
  print(f"total debit amount={result.debits}")
  print(f"autopays started={result.started}")
  print(f"autopays ended={result.ended}")
  print(f"balance for user {USER}={result.balance}")

display(process_log())
