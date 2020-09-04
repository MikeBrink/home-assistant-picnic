# Home Assistant component for Picnic.app

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

## This library is still in development

Provides Home Assistant sensors for Picnic (Supermarket) based on the [python-picnic-api](https://github.com/MikeBrink/python-picnic-api) repository.

This library is not affiliated with Picnic and retrieves data from the endpoints of the mobile application. Use at your own risk.

## Install
Use HACS to install these sensors or copy the files in the /custom_components/picnic/ folder to [homeassistant]/config/custom_components/picnic/

Example config:

```yaml
  sensor:
    - platform: picnic
      username: <username>            (required)
      password: <password>            (required)
      country_code: "NL"              (optional) (Choose from "NL" or "DE")
```

## Sensors
You will have three sensors available. 

#### Basket
The sensor `picnic_basket` indicates how many items you still have within your basket. Within the more dialog window you will also see the outstanding costs that you have.

#### Deliveries
PLACEHOLDER

#### Time Slots
The sensor `picnic_delivery_time_slots` indicates the first available delivery time slot. Within the attributes (more info dialog), you can also see all other available delivery time slots.

## Debugging
If you experience unexpected output, please create an issue with additional logging. You can add the following lines to enable logging

```
logger:
  default: error
  logs:
      custom_components.picnic: debug
```


[buymecoffee]: https://www.buymeacoffee.com/MikeBrink
[buymecoffeebadge]: https://camo.githubusercontent.com/cd005dca0ef55d7725912ec03a936d3a7c8de5b5/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f6275792532306d6525323061253230636f666665652d646f6e6174652d79656c6c6f772e737667
