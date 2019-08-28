
import WindowsVersionFile

result = fill_in_version_file_template(
  filevers = (0, 4, 40, 1),
  prodvers = (0, 4, 0, 0),
  datetime = 0,
  CompanyName = 'Seven Smiles :)',
  FileDescription = 'rFactor 2 Headlights Control',
  InternalName = 'rFactor 2 Headlight Control',
  LegalCopyright = '(c) 2019 Tony Whitley. All rights reserved.',
  OriginalFilename = 'rF2headlights.exe',
  ProductName = 'rF2headlights'
  )
print(result)