# Certificate Expiry
### Description
Generates sensor with the number of days left for a certificate to get expired

### How to set it up:

#### Basic configuration
* Configuration should be done via Configuration -> Integrations.
* In case you are already using that integration with YAML Configuration - please removed it
* Integration supports **multiple** certificates 
* In the setup form, the following details are mandatory:
  * Name - Unique
  * Path to the certificate

###### Sensors
```
Name: {Integration Name}
State: Number of days until certificate will expire
Attributes
    Path
    Issuer
    Subject
    Version
```
