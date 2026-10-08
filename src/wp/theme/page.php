<?php
/**
 * Other WordPress pages (not part of the prebuilt set).
 */
defined( 'ABSPATH' ) || exit;

vl_generic(
	function () {
		while ( have_posts() ) :
			the_post();
			?>
<section class="page-hero">
    <div class="wrap">
      <div class="sec-head">
        <h1><?php the_title(); ?></h1>
      </div>
      <div class="legal glasswrap prose">
        <?php the_content(); ?>
      </div>
    </div>
  </section>
			<?php
		endwhile;
	}
);
