<?php
/**
 * Blog index, archives and search results.
 */
defined( 'ABSPATH' ) || exit;

vl_generic(
	function () {
		if ( is_home() ) {
			$title = 'Geschichten aus der <span class="hl">Praxis</span>';
			$lead  = 'Kurze Geschichten aus meiner Arbeit mit Kindern, Eltern, Paaren und Erwachsenen.';
		} elseif ( is_search() ) {
			$title = 'Suche: ' . esc_html( get_search_query() );
			$lead  = '';
		} else {
			$title = wp_kses_post( get_the_archive_title() );
			$lead  = '';
		}
		?>
<section class="page-hero">
    <div class="wrap">
      <div class="sec-head">
        <span class="eyebrow">Blog</span>
        <h1><?php echo $title; // phpcs:ignore WordPress.Security.EscapeOutput -- escaped above ?></h1>
		<?php if ( $lead ) : ?>
        <p class="lead" style="margin-top:18px;max-width:640px"><?php echo esc_html( $lead ); ?></p>
		<?php endif; ?>
      </div>
      <div class="post-list">
		<?php if ( have_posts() ) : ?>
			<?php
			while ( have_posts() ) :
				the_post();
				?>
        <article class="post-card glasswrap">
          <p class="post-date"><?php echo esc_html( get_the_date() ); ?></p>
          <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
          <p class="muted"><?php echo esc_html( wp_trim_words( wp_strip_all_tags( get_the_content() ), 32 ) ); ?></p>
          <p style="margin-top:12px"><a class="txt-link" href="<?php the_permalink(); ?>">Weiterlesen <span class="arw" aria-hidden="true">→</span></a></p>
        </article>
			<?php endwhile; ?>
			<?php the_posts_pagination( array( 'mid_size' => 1 ) ); ?>
		<?php else : ?>
        <p class="muted">Hier gibt es noch keine Beiträge.</p>
		<?php endif; ?>
      </div>
    </div>
  </section>
		<?php
	}
);
