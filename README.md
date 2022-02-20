# ARPANSA UV Values Custom Component for Home Assistant

![GitHub Pipenv locked Python version](https://img.shields.io/github/pipenv/locked/python-version/joshuar/ha_arpansa_uv)
![GitHub last commit](https://img.shields.io/github/last-commit/joshuar/ha_arpansa_uv)

This is a simple custom component for Home Assistant that fetches the UV values from the [ARPANSA site](https://www.arpansa.gov.au/our-services/monitoring/ultraviolet-radiation-monitoring/ultraviolet-radation-data-information). 

## Installation

HACS method coming. For now, manually install by copying the files in a new `custom_components/arpansa_uv` directory.

## Configuration

After you have installed the custom component (see above):

1. Go to the `Configuration` -> `Integrations` page.
2. On the bottom right of the page, click on the `+ Add Integration` sign to add an integration
3. Search for ***ARPANSA UV*** (If you don't see it, try refreshing your browser page to reload the cache.)
4. Add a name for the integration (just for identification purposes on the integration page) and the stations you want to monitor
5. Click Submit to add the integration

The component will create sensors for each station with `<name>_uv_index`. Recommended using the statistics graph lovelace card.

## Troubleshooting

Please set your logging for the custom_component to debug:

```yaml
logger:
  default: warn
  logs:
    custom_components.arpansa_uv: debug
```

## Credits

[Ultraviolet icons created by Freepik - Flaticon](https://www.flaticon.com/free-icons/ultraviolet)