<?php
/**
 * Renders one of the theme's prebuilt pages (pages/<key>.html).
 *
 * The page already contains its title, meta tags and structured data; WordPress
 * adds only what wp_head()/wp_footer() print (admin bar and the scripts of the
 * plugins that the page uses, see VL_PLUGIN_ASSETS).
 */
defined( 'ABSPATH' ) || exit;

$vl_html = file_get_contents( get_theme_file_path( 'pages/' . vl_key() . '.html' ) );

// shortcodes first, so that the plugins can enqueue their scripts before wp_head()
$vl_html = preg_replace_callback(
	'/<!--SC:(\[.+?\])-->/s',
	function ( $m ) {
		return do_shortcode( $m[1] );
	},
	$vl_html
);

ob_start();
wp_head();
$vl_head = ob_get_clean();

ob_start();
wp_footer();
$vl_foot = ob_get_clean();

echo str_replace( // phpcs:ignore WordPress.Security.EscapeOutput -- prebuilt markup
	array( '<!--WP_HEAD-->', '<!--WP_FOOTER-->', '<body>' ),
	array( $vl_head, $vl_foot, '<body' . vl_body_class_attr() . '>' ),
	$vl_html
);
