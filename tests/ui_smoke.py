from __future__ import annotations

import re
from pathlib import Path

from playwright.sync_api import sync_playwright


ARTIFACTS = Path("artifacts")
ARTIFACTS.mkdir(exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
    console_errors: list[str] = []
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)

    page.goto("http://127.0.0.1:8510", wait_until="networkidle")
    initial_button = page.get_by_role("button", name="Carregar base inicial")
    page.get_by_text("Consumo e estoque imobiliário", exact=True).first.wait_for(timeout=30_000)
    if page.get_by_text("Comece pela carga inicial", exact=True).count():
        initial_button.wait_for(state="visible", timeout=8_000)
        initial_button.click()
        page.get_by_text("59.139", exact=True).wait_for(timeout=60_000)

    page.wait_for_timeout(3_000)
    page.screenshot(path=str(ARTIFACTS / "dashboard-overview.png"), full_page=True)

    page.get_by_text("Blocos e prumadas", exact=True).click()
    page.wait_for_timeout(3_000)
    page.get_by_text("Digite para buscar um empreendimento", exact=True).click()
    page.keyboard.type("ALAMEDA IMPERIAL")
    page.get_by_text("ALAMEDA IMPERIAL", exact=True).last.click()
    page.get_by_text("Compare os blocos", exact=True).wait_for(timeout=30_000)
    page.get_by_text("Abra o espelho do bloco", exact=True).wait_for(timeout=30_000)
    page.wait_for_timeout(3_000)
    page.screenshot(path=str(ARTIFACTS / "dashboard-floors.png"), full_page=True)
    page.get_by_text("Abra o espelho do bloco", exact=True).scroll_into_view_if_needed()
    page.wait_for_timeout(1_500)
    page.screenshot(path=str(ARTIFACTS / "dashboard-building-grid.png"), full_page=False)
    page.locator(".js-plotly-plot").last.scroll_into_view_if_needed()
    page.wait_for_timeout(1_000)
    page.screenshot(path=str(ARTIFACTS / "dashboard-building-map.png"), full_page=False)
    page.locator(".js-plotly-plot").last.locator(".scatterlayer .point").first.click(force=True)
    page.get_by_text(re.compile(r"^Unidade \d+$")).wait_for(timeout=30_000)

    page.get_by_text("Detalhe do empreendimento", exact=True).click()
    page.get_by_text("Distribuição por andar", exact=True).wait_for(timeout=30_000)
    page.screenshot(path=str(ARTIFACTS / "dashboard-enterprise.png"), full_page=True)

    page.get_by_text("Velocidade", exact=True).click()
    page.get_by_text("Velocidade indisponível", exact=True).wait_for(timeout=30_000)

    page.get_by_text("Qualidade dos dados", exact=True).click()
    page.get_by_text("Resumo dos alertas", exact=True).wait_for(timeout=30_000)
    page.screenshot(path=str(ARTIFACTS / "dashboard-quality.png"), full_page=True)

    print(f"title={page.title()}")
    print(f"console_errors={console_errors}")
    print(f"screenshots={sorted(str(path) for path in ARTIFACTS.glob('dashboard-*.png'))}")
    app_errors = [
        error
        for error in console_errors
        if "metrics config" not in error
        and "ERR_NETWORK_ACCESS_DENIED" not in error
        and "Undefined metrics config" not in error
    ]
    assert not app_errors, app_errors
    browser.close()
