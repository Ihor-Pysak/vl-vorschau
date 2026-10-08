<?php
/**
 * Theme "Viktoria Langjahr".
 *
 * The main pages are built outside WordPress (src/build.py) and shipped in
 * pages/*.html; vl-static.php prints them. Blog posts, the blog index and any
 * other WordPress page use the same header and footer (parts/generic.html).
 */
defined( 'ABSPATH' ) || exit;

// WordPress page slug => prebuilt page (pages/<key>.html)
const VL_PAGES = array(
	'coaching-fuer-kinder-und-jugendliche' => 'coaching-kinder',
	'coaching-fuer-eltern'                 => 'coaching-eltern',
	'coaching-fuer-paare'                  => 'coaching-paare',
	'coaching-fuer-erwachsene'             => 'coaching-erwachsene',
	'so-arbeite-ich'                       => 'so-arbeite-ich',
	'kurse'                                => 'kurse',
	'ueber-mich'                           => 'ueber-mich',
	'sos-elternkurs'                       => 'sos-elternkurs',
	'akademie'                             => 'akademie',
	'kontakt'                              => 'kontakt',
	'onlinereservierung'                   => 'onlinereservierung',
	'impressum'                            => 'impressum',
	'datenschutzerklarung'                 => 'datenschutzerklarung',
);

// old Russian site (ru.viktoria-langjahr.de): page slug => page on the German site
const VL_RU_PATHS = array(
	'kouching-dlya-detej-i-podrostkov' => '/coaching-fuer-kinder-und-jugendliche/',
	'kouching-dlya-roditelej'          => '/coaching-fuer-eltern/',
	'kouching-dlya-par'                => '/coaching-fuer-paare/',
	'pro-menya'                        => '/ueber-mich/',
	'akademiya'                        => '/akademie/',
	'mentorstvo'                       => '/kurse/',
	'informacziya'                     => '/so-arbeite-ich/',
	'bronirovanie-onlajn'              => '/onlinereservierung/',
	'impressum'                        => '/impressum/',
	'datenschutzerklarung'             => '/datenschutzerklarung/',
	'blog'                             => '/blog/',
	'2022/04/25'                       => '/2022/04/25/konzentrationsprobleme-amelies-geschichte/',
	'2022/05/18'                       => '/2022/05/18/aggression-simons-geschichte/',
	'2022/06/11'                       => '/2022/06/11/nervoese-ticks-die-geschichte-von-allesandro/',
	'2022/10/22'                       => '/2022/10/22/angst-vor-dem-alleinsein-und-vor-ohnmacht/',
	'2022/12/02'                       => '/2022/12/02/praxisgeschichte-eines-paares/',
);

// IndexNow key (Bing and others): served as /<key>.txt, used to announce updated URLs
const VL_INDEXNOW_KEY = 'cbc496af89673c87a91a4c9feaac26b6';

// pages of the old site that no longer exist
const VL_REDIRECTS = array(
	'coaching'      => '/',
	'mentoring'     => '/kurse/',
	'informationen' => '/so-arbeite-ich/',
);

// plugins whose scripts and styles a prebuilt page may load; everything else is dropped
const VL_PLUGIN_ASSETS = array(
	'onlinereservierung' => array( 'team-booking' ),
	'kontakt'            => array( 'contact-form-7', 'honeypot' ),
);

// Contact Form 7: no automatic <p>/<br> in the form markup
add_filter( 'wpcf7_autop_or_not', '__return_false' );

add_action(
	'after_setup_theme',
	function () {
		add_theme_support( 'title-tag' );
		add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );

		remove_action( 'wp_head', 'print_emoji_detection_script', 7 );
		remove_action( 'wp_print_styles', 'print_emoji_styles' );
		remove_action( 'wp_head', 'wp_generator' );
		remove_action( 'wp_head', 'rsd_link' );
		remove_action( 'wp_head', 'wlwmanifest_link' );
		remove_action( 'wp_head', 'wp_shortlink_wp_head' );
		remove_action( 'wp_head', 'rest_output_link_wp_head' );
		remove_action( 'wp_head', 'wp_oembed_add_discovery_links' );
		remove_action( 'wp_head', 'feed_links_extra', 3 );
		remove_action( 'wp_head', 'wp_site_icon', 99 ); // the theme brings its own favicon
	}
);

/**
 * Key of the prebuilt page for the current request, or null.
 */
function vl_key() {
	if ( is_front_page() ) {
		$key = 'index';
	} elseif ( is_page() ) {
		$slug = get_post_field( 'post_name', get_queried_object_id() );
		$key  = isset( VL_PAGES[ $slug ] ) ? VL_PAGES[ $slug ] : null;
	} else {
		$key = null;
	}
	if ( $key && ! file_exists( get_theme_file_path( 'pages/' . $key . '.html' ) ) ) {
		$key = null;
	}
	return $key;
}

function vl_body_class_attr() {
	return is_admin_bar_showing() ? ' class="admin-bar"' : '';
}

function vl_blog_url() {
	$id = (int) get_option( 'page_for_posts' );
	return $id ? get_permalink( $id ) : home_url( '/' );
}

/**
 * Other host names of the web space (www, ru, old, test, ...) can point to this WordPress.
 * Send every such request to the same page on the main domain; old Russian pages go to
 * their German counterparts.
 */
add_action(
	'init',
	function () {
		if ( ( defined( 'WP_CLI' ) && WP_CLI ) || wp_doing_cron() || empty( $_SERVER['HTTP_HOST'] ) ) {
			return;
		}
		$main = wp_parse_url( home_url(), PHP_URL_HOST );
		$host = strtolower( preg_replace( '/:\d+$/', '', wp_unslash( $_SERVER['HTTP_HOST'] ) ) ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
		if ( ! $main || $host === $main ) {
			return;
		}
		$uri  = isset( $_SERVER['REQUEST_URI'] ) ? wp_unslash( $_SERVER['REQUEST_URI'] ) : '/'; // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
		$path = (string) wp_parse_url( $uri, PHP_URL_PATH );
		if ( 0 === strpos( $host, 'ru.' ) ) {
			$key    = trim( $path, '/' );
			$target = '/';
			foreach ( VL_RU_PATHS as $from => $to ) {
				if ( $key === $from || 0 === strpos( $key, $from . '/' ) ) {
					$target = $to;
					break;
				}
			}
		} else {
			$target = '' === $path ? '/' : $path;
		}
		wp_redirect( home_url( $target ), 301, 'Viktoria Langjahr' ); // phpcs:ignore WordPress.Security.SafeRedirect
		exit;
	},
	0
);

// llms.txt for AI assistants, redirects of removed pages
add_action(
	'template_redirect',
	function () {
		$path = trim( (string) wp_parse_url( isset( $_SERVER['REQUEST_URI'] ) ? wp_unslash( $_SERVER['REQUEST_URI'] ) : '', PHP_URL_PATH ), '/' ); // phpcs:ignore WordPress.Security.ValidatedSanitizedInput
		if ( 'llms.txt' === $path ) {
			status_header( 200 );
			header( 'Content-Type: text/plain; charset=utf-8' );
			readfile( get_theme_file_path( 'llms.txt' ) ); // phpcs:ignore WordPress.WP.AlternativeFunctions
			exit;
		}
		if ( VL_INDEXNOW_KEY . '.txt' === $path ) {
			status_header( 200 );
			header( 'Content-Type: text/plain; charset=utf-8' );
			echo VL_INDEXNOW_KEY; // phpcs:ignore WordPress.Security.EscapeOutput
			exit;
		}
		if ( isset( VL_REDIRECTS[ $path ] ) ) {
			wp_safe_redirect( home_url( VL_REDIRECTS[ $path ] ), 301 );
			exit;
		}
	},
	0
);

// prebuilt pages bring their own title, meta tags and structured data
add_action(
	'template_redirect',
	function () {
		if ( ! vl_key() ) {
			return;
		}
		add_filter( 'wpseo_frontend_presenters', '__return_empty_array' );
		add_filter( 'wpseo_json_ld_output', '__return_false' );
		add_filter( 'wpseo_debug_markers', '__return_false' );
		remove_action( 'wp_head', '_wp_render_title_tag', 1 );
		remove_action( 'wp_head', 'rel_canonical' );
	},
	20
);

add_filter(
	'template_include',
	function ( $template ) {
		return vl_key() ? get_theme_file_path( 'vl-static.php' ) : $template;
	},
	99
);

/**
 * Drop the scripts and styles of the old theme, Elementor and other plugins;
 * the site has its own stylesheet. Only the admin bar and the plugins listed in
 * VL_PLUGIN_ASSETS for the current page are kept.
 */
function vl_trim_assets() {
	if ( is_admin() ) {
		return;
	}
	$key     = vl_key();
	$plugins = ( $key && isset( VL_PLUGIN_ASSETS[ $key ] ) ) ? VL_PLUGIN_ASSETS[ $key ] : array();
	$keep    = is_admin_bar_showing() ? array( 'admin-bar', 'dashicons' ) : array();
	foreach ( array( wp_styles(), wp_scripts() ) as $reg ) {
		foreach ( (array) $reg->queue as $handle ) {
			if ( in_array( $handle, $keep, true ) ) {
				continue;
			}
			$src = isset( $reg->registered[ $handle ] ) ? (string) $reg->registered[ $handle ]->src : '';
			$ok  = false;
			foreach ( $plugins as $p ) {
				if ( '' !== $src && false !== strpos( $src, '/plugins/' . $p . '/' ) ) {
					$ok = true;
				}
			}
			if ( ! $ok ) {
				$reg->dequeue( $handle );
			}
		}
	}
}
add_action( 'wp_enqueue_scripts', 'vl_trim_assets', PHP_INT_MAX );
add_action( 'wp_print_styles', 'vl_trim_assets', PHP_INT_MAX );
add_action( 'wp_print_footer_scripts', 'vl_trim_assets', 1 );

// Yoast on the blog: title and description for the blog index, a description from the text for posts
add_filter(
	'wpseo_title',
	function ( $title ) {
		return is_home() ? 'Geschichten aus der Praxis – Viktoria Langjahr' : $title;
	}
);
function vl_blog_description( $desc ) {
	if ( is_home() ) {
		return 'Geschichten aus der Praxis: kurze Fallgeschichten aus der psychoemotionalen Begleitung von Kindern, Eltern, Paaren und Erwachsenen in Olpe.';
	}
	if ( is_singular( 'post' ) && ! $desc ) {
		return wp_trim_words( wp_strip_all_tags( get_post_field( 'post_content', get_queried_object_id() ) ), 24, ' …' );
	}
	return $desc;
}
add_filter( 'wpseo_metadesc', 'vl_blog_description' );
add_filter( 'wpseo_opengraph_desc', 'vl_blog_description' );
add_filter(
	'wpseo_opengraph_title',
	function ( $title ) {
		return is_home() ? 'Geschichten aus der Praxis – Viktoria Langjahr' : $title;
	}
);

/**
 * TheBooking: in emails, choice fields (select/radio) always showed "Nicht ausgewählt".
 * The plugin looks up $option['value'], but the options of this form only have a label
 * (created with an older plugin version). Fill in the label of the chosen option instead.
 */
add_filter(
	'tbk_notification_templates',
	function ( $values, $reservation_id ) {
		if ( ! is_array( $values ) || ! class_exists( '\VSHM\Providers\FormEntries' ) || ! class_exists( '\VSHM\Providers\FormFields' ) ) {
			return $values;
		}
		try {
			foreach ( (array) \VSHM\Providers\FormEntries::provideBy( array( 'reservationId' => $reservation_id ) ) as $entry ) {
				if ( ! is_array( $entry ) || ! isset( $entry['id'], $entry['value'] ) ) {
					continue;
				}
				$field = \VSHM\Providers\FormFields::provideBy( array( 'id' => $entry['id'] ), true );
				if ( ! is_array( $field ) || ! in_array( $field['type'] ?? '', array( 'select', 'radio' ), true ) || empty( $field['hook'] ) ) {
					continue;
				}
				$option = $field['data']['options'][ $entry['value'] ] ?? null;
				if ( is_array( $option ) && empty( $option['value'] ) && ! empty( $option['label'] ) ) {
					$values[ $field['hook'] ] = $option['label'];
				}
			}
		} catch ( \Throwable $e ) {
			return $values;
		}
		return $values;
	},
	20,
	2
);

/**
 * Emails from the site are sent from info@viktoria-langjahr.de (own domain, against spam), but that
 * mailbox is not read. Replies should reach Viktoria directly: add a Reply-To with her address unless
 * the email already has one (the contact form sets the visitor) or is addressed to her own addresses.
 */
add_filter(
	'wp_mail',
	function ( $args ) {
		$own = array( 'viktorialangjahr@gmx.de', 'v.langjahr@gmx.de', 'info@viktoria-langjahr.de' );
		$to  = is_array( $args['to'] ) ? $args['to'] : explode( ',', (string) $args['to'] );
		foreach ( $to as $addr ) {
			$addr = strtolower( trim( preg_replace( '/^.*<([^>]+)>.*$/', '$1', (string) $addr ) ) );
			if ( in_array( $addr, $own, true ) ) {
				return $args;
			}
		}
		$headers = isset( $args['headers'] ) ? $args['headers'] : '';
		$all     = is_array( $headers ) ? implode( "\n", $headers ) : (string) $headers;
		if ( false !== stripos( $all, 'reply-to:' ) ) {
			return $args;
		}
		$line = 'Reply-To: Viktoria Langjahr <viktorialangjahr@gmx.de>';
		if ( is_array( $headers ) ) {
			$headers[] = $line;
		} else {
			$headers = '' === trim( $all ) ? $line : rtrim( $all ) . "\r\n" . $line;
		}
		$args['headers'] = $headers;
		return $args;
	}
);

// no share buttons from AddToAny in blog posts
add_filter( 'addtoany_sharing_disabled', '__return_true' );

/**
 * Removes what other plugins (mostly Elementor) print into wp_head()/wp_footer()
 * although the page does not use them: generator tags, the Google Fonts
 * preconnect (no connection to Google without consent), lazy-load helpers and
 * old favicons from the media library.
 *
 * @param string $html Output of wp_head() or wp_footer().
 * @return string
 */
function vl_clean( $html ) {
	$out = preg_replace(
		array(
			'#<meta name=["\']generator["\'][^>]*>\s*#i',
			'#<link[^>]+(?:fonts\.gstatic\.com|fonts\.googleapis\.com)[^>]*>\s*#i',
			'#<link rel=["\'](?:icon|apple-touch-icon)["\'][^>]+/wp-content/uploads/[^>]*>\s*#i',
			'#<meta name=["\']msapplication-TileImage["\'][^>]*>\s*#i',
		),
		'',
		$html
	);
	if ( null === $out ) { // regex error: better unfiltered than empty
		return $html;
	}
	// Elementor's lazy-load helpers: drop whole <script>/<style> blocks by their content
	$out2 = preg_replace_callback(
		'#<(script|style)\b[^>]*>.*?</\1>\s*#is',
		function ( $m ) {
			$drop = false !== strpos( $m[0], 'lazyloadRunObserver' ) || false !== strpos( $m[0], '.e-con.e-parent' );
			return $drop ? '' : $m[0];
		},
		$out
	);
	return null === $out2 ? $out : $out2;
}

/**
 * Prints a WordPress page in the site layout (parts/generic.html).
 *
 * @param callable $content Prints the content of <main>.
 */
function vl_generic( callable $content ) {
	$tpl = file_get_contents( get_theme_file_path( 'parts/generic.html' ) ); // phpcs:ignore WordPress.WP.AlternativeFunctions
	list( $top, $bottom ) = explode( '<!--CONTENT-->', $tpl, 2 );

	ob_start();
	wp_head();
	$head = vl_clean( ob_get_clean() );
	echo str_replace( array( '<!--WP_HEAD-->', '<body>' ), array( $head, '<body' . vl_body_class_attr() . '>' ), $top ); // phpcs:ignore WordPress.Security.EscapeOutput

	$content();

	ob_start();
	wp_footer();
	$foot = vl_clean( ob_get_clean() );
	echo str_replace( '<!--WP_FOOTER-->', $foot, $bottom ); // phpcs:ignore WordPress.Security.EscapeOutput
}

// editing a page in the admin has no effect when the theme renders it: say so
add_action(
	'admin_notices',
	function () {
		$screen = get_current_screen();
		if ( ! $screen || 'page' !== $screen->post_type || 'post' !== $screen->base ) {
			return;
		}
		$post = get_post();
		if ( ! $post ) {
			return;
		}
		$front = (int) get_option( 'page_on_front' ) === (int) $post->ID;
		if ( $front || isset( VL_PAGES[ $post->post_name ] ) ) {
			echo '<div class="notice notice-info"><p><strong>Hinweis:</strong> Der Inhalt dieser Seite kommt aus dem Theme „Viktoria Langjahr“. Änderungen hier im Editor werden auf der Website nicht angezeigt.</p></div>';
		}
	}
);
