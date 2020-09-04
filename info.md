## Home Assistant sensor component for Picnic.app

Provides Home Assistant sensors for Picnic.app (Online Supermarket).

### Example config:

```yaml
  sensor:
    - platform: picnic
      username: <username>            (required)
      password: <password>            (required)
      country_code: "NL"              (optional) (Choose from "NL" or "DE")
```

[For more information visit the repository.](https://raw.githubusercontent.com/MikeBrink/home-assistant-picnic/)
