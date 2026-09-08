<?php
/**
 * WPCode 스니펫 1001 — "Rank Math REST meta — KoreaPlug"
 * ---------------------------------------------------------------------------
 * 목적
 *   wordpress_draft 루틴이 브라우저 로그인 없이 Rank Math 의 포커스 키워드 /
 *   SEO 타이틀 / 메타 설명을 저장할 수 있도록, 해당 포스트 메타를 REST API 에
 *   노출한다. Rank Math 는 이 메타들을 show_in_rest 없이 등록하기 때문에
 *   기본 상태에서는 REST 로 읽지도 쓰지도 못한다.
 *
 * 설치 (WPCode Lite)
 *   코드 스니펫 → 새로 추가 → 사용자 정의 코드 추가
 *   제목   : Rank Math REST meta — KoreaPlug
 *   유형   : PHP 스니펫
 *   삽입   : 자동 삽입 → 어디서나 실행 (Run Everywhere)
 *   상태   : 활성
 *   ※ AdSense 스니펫 999 와 합치지 않는다. 「헤더 및 푸터」 전역 블록에도 넣지 않는다.
 *
 * 보안
 *   - 쓰기는 해당 글의 편집 권한(edit_post)이 있는 사용자로 제한한다.
 *     앱 비밀번호 Basic Auth 도 이 검사를 통과해야 한다.
 *   - rank_math_seo_score 는 읽기 전용이다. 에디터 JS 가 계산해 넣는 값이라
 *     루틴이 임의로 쓰면 실제 품질과 무관한 숫자가 기록된다.
 *   - 대상 포스트 타입은 'post' 하나로 한정한다.
 *
 * 검증 (설치 직후 1회)
 *   curl -s -u "$U:$P" \
 *     "https://koreaplug.com/wp-json/wp/v2/posts/{ID}?context=edit&_fields=meta" \
 *     | grep -c rank_math_focus_keyword      # 1 이상이면 정상
 *   이미 UI 로 키워드를 넣어 둔 글로 확인하면, 반환된 값이 그 키워드와 같은지까지
 *   한 번에 볼 수 있다.
 *
 * 관련 지침: KoreaPlug-Draft.md 5-6 (v10.6, 2026-09-08 신설)
 */

add_action(
	'init',
	function () {

		// Rank Math 자신의 register_meta 가 끝난 뒤에 덮어써야 하므로 우선순위를 늦춘다.
		$writable = array(
			'rank_math_focus_keyword',
			'rank_math_title',
			'rank_math_description',
		);

		foreach ( $writable as $key ) {
			register_post_meta(
				'post',
				$key,
				array(
					'type'              => 'string',
					'single'            => true,
					'default'           => '',
					'show_in_rest'      => true,
					'sanitize_callback' => function ( $value ) {
						if ( ! is_string( $value ) ) {
							return '';
						}
						// 태그 제거 + 개행 정리. 키워드 구분자 ',' 는 보존한다.
						$value = wp_strip_all_tags( $value );
						return trim( preg_replace( '/\s+/u', ' ', $value ) );
					},
					'auth_callback'     => function ( $allowed, $meta_key, $post_id ) {
						return current_user_can( 'edit_post', $post_id );
					},
				)
			);
		}

		// 점수는 노출만 하고 쓰기는 막는다.
		register_post_meta(
			'post',
			'rank_math_seo_score',
			array(
				'type'          => 'string',
				'single'        => true,
				'default'       => '',
				'show_in_rest'  => true,
				'auth_callback' => '__return_false',
			)
		);
	},
	99
);
