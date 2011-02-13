/*!
 * OuterHTML v1.0.0 (Release version)
 *
 * http://www.darlesson.com/
 *
 * Copyright 2010, Darlesson Oliveira
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 * @requires jQuery v1.4.0 or above
 *
 * Reporting bugs, comments or suggestions: http://darlesson.com/contact/
 * Documentation and other jQuery plug-ins: http://darlesson.com/jquery/
 * Donations are welcome: http://darlesson.com/donate/
 */
 
// Examples and documentation at: http://darlesson.com/jquery/outerhtml/

// jQuery outerHTML
(function($){
		  
	$.fn.extend({
		outerHTML : function( value ){
	
			// Replaces the content
			if( typeof value === "string" ){
				var $this = $(this),
					$parent = $this.parent();
					
				var replaceElements = function(){
					
					// For some reason sometimes images are not replaced properly so we get rid of them first
					var $img = $this.find("img");
					if( $img.length > 0 ){
						$img.remove();
					}
					
					var element;
					$( value ).map(function(){
						element = $(this);
						$this.replaceWith( element );
					})
					
					return element;
					
				}
				
				return replaceElements();
				
			// Returns the value
			}else{
				return $("<div />").append($(this).clone()).html();
			}
	
		}
	});

})(jQuery);
