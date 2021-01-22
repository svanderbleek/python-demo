import csv
import sys
import collections

SLCSP_CSV = "slcsp.csv"
ZIPS_CSV = "zips.csv"
PLANS_CSV = "plans.csv"

PLANS_SILVER = "Silver"

CSV_SAMPLE_BYTES = 1024
CSV_START_BYTE = 0

def csv_sniffer_has_header(file):
  sample = file.read(CSV_SAMPLE_BYTES)
  file.seek(CSV_START_BYTE)

  has_header = csv.Sniffer().has_header(sample)
  return has_header
  
def read_csv_header_rows(name):
  header = None

  with open(name) as file:
    has_header = csv_sniffer_has_header(file)
    reader = csv.reader(file)

    if has_header:
      header, *rows = reader
    else:
      rows = list(reader)

  return (header, rows)

def second_lowest(rates):
  """
  >>> second_lowest([]) is None
  True

  >>> second_lowest([1]) is None
  True

  >>> second_lowest([1, 1]) is None
  True

  >>> second_lowest([1, 2])
  2

  >>> second_lowest([2, 1])
  2

  >>> second_lowest([197.3, 197.3, 201.1, 305.4, 306.7, 411.24])
  201.1
  """

  unique_rates = set(rates) 
  try:
    unique_rates.remove(min(unique_rates))
    return min(unique_rates)
  except ValueError:
    return None

def parse_rate(rate):
  try:
    return float(rate)
  except ValueError:
    return None

def format_rate(rate):
  if rate:
    rate = "{:0.2f}".format(rate)
  return rate

def state_rate_area_rates_lookup(plans_rows):
  state_rate_area_rates = collections.defaultdict(list)

  for plans_row in plans_rows:
    _, state, metal_level, rate, rate_area = plans_row
    if metal_level == PLANS_SILVER:
      rate = parse_rate(rate)
      if rate:
        state_rate_area_rates[(state, rate_area)].append(rate)

  return state_rate_area_rates

def state_rate_area_rate_lookup(plans_rows):
  state_rate_area_rates = state_rate_area_rates_lookup(plans_rows)
  state_rate_area_rate = collections.defaultdict(str)

  for state_rate_area, rates in state_rate_area_rates.items():
    rate = second_lowest(rates)
    if rate:
      state_rate_area_rate[state_rate_area] = rate

  return state_rate_area_rate

def zipcode_rate_lookup(zips_rows, plans_rows):
  zipcode_rate = collections.defaultdict(str)
  zipcode_state_rate_areas = collections.defaultdict(set)
  state_rate_area_rate = state_rate_area_rate_lookup(plans_rows)

  for zips_row in zips_rows:
    zipcode, state, _, _, rate_area = zips_row
    state_rate_area = (state, rate_area)
    zipcode_state_rate_areas[zipcode].add(state_rate_area)

    if len(zipcode_state_rate_areas[zipcode]) > 1:
      zipcode_rate[zipcode] = ""
    else:
      zipcode_rate[zipcode] = state_rate_area_rate[state_rate_area]

  return zipcode_rate

def zipcode(slcsp_row):
  return slcsp_row[0]

def zipcode_with_rate(slcsp_rows, zipcode_rate):
  return [[zipcode(row), format_rate(zipcode_rate[zipcode(row)])] for row in slcsp_rows]

def find_slcsp_and_write_to_stdout():
  slcsp_header, slcsp_rows =  read_csv_header_rows(SLCSP_CSV)
  _, zips_rows =  read_csv_header_rows(ZIPS_CSV)
  _, plans_rows =  read_csv_header_rows(PLANS_CSV)

  zipcode_rate = zipcode_rate_lookup(zips_rows, plans_rows)

  slcsp_rows = zipcode_with_rate(slcsp_rows, zipcode_rate)

  writer = csv.writer(sys.stdout)
  writer.writerows([slcsp_header] + slcsp_rows)

find_slcsp_and_write_to_stdout()
