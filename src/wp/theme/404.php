<?php
/**
 * Page not found.
 */
defined( 'ABSPATH' ) || exit;

vl_generic(
	function () {
		?>
<section class="page-hero">
    <div class="wrap">
      <div class="sec-head">
        <span class="eyebrow">Seite nicht gefunden</span>
        <h1>Diese Seite gibt es <span class="hl">nicht mehr</span>.</h1>
        <p class="lead" style="margin-top:18px;max-width:640px">Vielleicht hat sich die Adresse geändert. Hier geht es weiter:</p>
      </div>
      <div class="btns" style="margin-top:26px">
        <a class="btn btn-primary" href="/">Zur Startseite</a>
        <a class="btn btn-glass" href="/kontakt/">Kontakt</a>
      </div>
    </div>
  </section>
		<?php
	}
);
