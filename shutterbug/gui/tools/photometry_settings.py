from shutterbug.gui.operators.base_settings import BaseSettings


class PhotometryOperatorSettingsWidget(BaseSettings):

    name = "Photometry"

    def _build_ui(self):
        """Builds UI for Photometry Operator settings"""
        pass


class PhotometryToolSettingsWidget(BaseSettings):

    name = "Photometry"

    def _build_ui(self):
        """Builds UI for Photometry Tool settings"""
        return None
