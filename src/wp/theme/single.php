<?php
/**
 * Blog post ("Geschichten aus der Praxis").
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
        <span class="eyebrow">Geschichten aus der Praxis</span>
        <h1><?php the_title(); ?></h1>
        <p class="post-date" style="margin-top:12px"><?php echo esc_html( get_the_date() ); ?></p>
      </div>
      <article class="post-body glasswrap prose">
        <?php the_content(); ?>
      </article>
      <div class="btns post-back">
        <a class="btn btn-glass" href="<?php echo esc_url( vl_blog_url() ); ?>">← Alle Geschichten</a>
        <a class="btn btn-primary" href="/kontakt/">Erstgespräch vereinbaren</a>
      </div>
    </div>
  </section>
			<?php
		endwhile;
	}
);
