class MockPhotoEnhancement:
    """
    Portfolio mock. Production swap: PhotoEnhancementService uses PIL to
    overlay branded text, captions, and logos onto uploaded images.

    Real interface (see INTEGRATIONS.md):
        apply_text_overlay(image_path, business_name, caption, industry,
                           brand_voice, platform, text_color) -> str
    """

    def apply_text_overlay(
        self,
        image_path: str,
        business_name: str = "",
        caption: str = "",
        industry: str = "",
        brand_voice: str = "",
        platform: str = "",
        text_color: str = None,
    ) -> str:
        return image_path
