# Fordpass Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/itchannel)

> [!WARNING]
> # Breaking Change
> There is a new token obtaining system.
> 
> The token used by this integration is currently removed whenever the integration is updated. With this 1.70 update, the token will be wiped during every update, requiring users to manually add the token during the initial setup.
> 
> To prevent this issue, we will be moving the token file outside of the FordPass directory. This change will ensure that the token is preserved during updates. This will require reconfiguration of your setup.
> Please see the Installation section, or the Wiki for help.

#### Please be aware that there may be issues or disruptions during this process.

If you have any questions or concerns, please either open a new issue or comment on an existing issue related to yours.

Thank you,

itchannel and SquidBytes


## Credit 
- https://github.com/clarkd - Initial Home Assistant automation idea and Python code (Lock/Unlock)
- https://github.com/pinballnewf - Figuring out the application ID issue
- https://github.com/degrashopper - Fixing 401 error for certain installs
- https://github.com/tonesto7 - Extra window statuses and sensors
- https://github.com/JacobWasFramed - Updated unit conversions
- https://github.com/heehoo59 - French Translation
- https://github.com/SquidBytes - EV updates and documentation

## **Changelog**
[Updates](info.md)

## Installation
Use [HACS](https://hacs.xyz/) to add this repository as a custom repo. 

Upon installation navigate to your integrations, and follow the configuration options. You will need to provide:
- Fordpass Email
- Region (Where you are based, required for tokens to work correctly)

You will then be prompted with `Setup Token` 

Follow the instructions on the [Wiki](https://github.com/itchannel/fordpass-ha/wiki/Obtaining-Tokens-(As-of-25-05-2024)) to obtain your token

## Usage
Your car must have the lastest onboard modem functionality and have registered/authorised the fordpass application

### Car Refresh
I have added a service to poll the car for updates, due to the battery drain I have left this up to you to set the interval. The service to be called is "refresh_status" and can be accessed in home assistant using "fordpas.refresh_status". 

Optionally you can add the "vin" parameter followed by your VIN number to only refresh one vehicle. By default this service will refresh all registered cars in HA.

**This will take up to 5 mins to update from the car once the service has been run**

### Clear Tokens
If you are experiencing any sign in issues, please trying clearing your tokens using the "clear_tokens" service call.

### Poll API
This service allows you to manually refresh/poll the API without waiting the set poll interval. Handy if you need quicker updates e.g. when driving for gps coordinates

## Sensors
### Currently Working
**Sensors may change as the integration is being developed**

- Fuel Level
- Odometer
- Lock/Unlock
- Oil Status
- Last known GPS Coordinates/Map
- Tyre Status
- Battery Status
- Ignition Status
- Alarm Status
- Individual door statuses
- Remote Start
- Window Status (Only if your car supports it!)
- Last Car Refresh status
- Car Tracker
- Supports Multiple Regions
- Electric Vehicle Support
- TPMS Sensors
- Guard Mode (Only supported cars)
- Deep sleep status
- Fordpass messages and alerts

## Disclaimer

This integration is not officially supported by Ford and as such using this integration could result in your account being locked out!
