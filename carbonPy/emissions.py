# carbon_py/emissions.py


class CarbonIntensityProvider:
    """
    Provides carbon intensity data (gCO₂eq/kWh).
    """

    # Source: IEA – International Energy Agency. Data for 2025.
    # Data represents grams of CO2 equivalent per kilowatt-hour (gCO₂eq/kWh).
    _INTENSITY_DATA = {
        # Europe
        "DE": 380,  # Germany (declining, but coal still retains a share)
        "GB": 145,  # Great Britain (active decommissioning of coal)
        "FR": 55,  # France (traditionally low due to nuclear power)
        "IT": 290,  # Italy
        "ES": 140,  # Spain (high share of solar generation)
        "PL": 650,  # Poland (gradual move away from coal, significant reduction)
        "NL": 310,  # Netherlands
        "SE": 12,  # Sweden (almost complete decarbonization)
        "NO": 10,  # Norway
        "FI": 50,  # Finland
        "DK": 85,  # Denmark
        "RU": 335,  # Russia (stable, slight increase in the share of gas)
        "CH": 25,  # Switzerland
        "AT": 80,  # Austria
        "BE": 135,  # Belgium
        "IE": 310,  # Ireland
        "PT": 150,  # Portugal
        "GR": 265,  # Greece (reached a historic low in 2025)
        # America
        "US": 355,  # USA (moderate decline, gas growth limits the fall)
        "CA": 105,  # Canada
        "BR": 85,  # Brazil (high share of hydropower)
        "MX": 410,  # Mexico
        "AR": 260,  # Argentina
        "CL": 145,  # Chile
        "CO": 90,  # Colombia
        # Asia and Oceania
        "CN": 525,  # China (noticeable reduction due to record commissioning of renewables)
        "IN": 680,  # India (intensity is falling, despite the growth in absolute emissions)
        "JP": 440,  # Japan
        "AU": 480,  # Australia (rapid adoption of solar panels)
        "KR": 395,  # South Korea
        "ID": 740,  # Indonesia
        "VN": 450,  # Vietnam
        "TH": 420,  # Thailand
        "MY": 560,  # Malaysia
        "PK": 480,  # Pakistan
        "NZ": 85,  # New Zealand
        # Other regions
        "ZA": 810,  # South Africa (remains one of the highest in the world)
        "TR": 430,  # Turkey
        "DEFAULT": 425,  # Global average (IEA forecast for 2025: ~415-430)
    }

    def get_intensity(self, region_code: str) -> int:
        """Returns the intensity for a region or the default value."""
        return self._INTENSITY_DATA.get(
            region_code.upper(), self._INTENSITY_DATA["DEFAULT"]
        )
