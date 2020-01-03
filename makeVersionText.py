
from WindowsVersionFile.WindowsVersionFile import fill_in_version_file_template

result = fill_in_version_file_template(
    filevers=(0, 6, 54, 0),
    prodvers=(0, 6, 0, 0),
    datetime=0,
    CompanyName='Seven Smiles :)',
    FileDescription='rFactor 2 Headlights Control',
    InternalName='rFactor 2 Headlight Control',
    LegalCopyright='(c) 2019 Tony Whitley. All rights reserved.',
    OriginalFilename='rF2headlights.exe',
    ProductName='rF2headlights'
)
print(result)
