/*global: data, jQuery, _, Showdown, throttle, Cache, tim */

var debug = true,
    namespace = "fluffbox",
    maxImageWidth = 500,
    maxImageHeight = 500,
    updateThrottle = 50,
    cacheSaveThrottle = 250,
    tweetTimeout = 60,
    markdown = new Showdown.converter(),
    cache = new Cache(namespace),

    // DOM
    //document = window.document,
    fluffElem = jQuery("#fluff"),
    editorElem = jQuery("#editor"),
    previewElem = jQuery("#preview"),
    twitterUserElem = jQuery("#twitter-username"),
    tweetsElem = jQuery("#tweets"),
    
    editorVal;


/////

function now(){
    return (new Date()).getTime();
}

function faveTweets(username, callback){
    var cacheNS = "favetweets-" + username,
        tweets = cache.wrapper(cacheNS);
        
    if (tweets && tweets.t + (tweetTimeout * 1000) < now()){
        return callback(tweets.v);
    }
    
    jQuery.getJSON("http://api.twitter.com/1/favorites/" + username + ".json?callback=?", function(data){
        cache.set(cacheNS, data);
        callback(data);
    });
}


function toHtml(content){
    return markdown.makeHtml(jQuery.trim(content));
}

function sortByTimestamp(a, b){
    return a.timestamp - b.timestamp;
}

// Modified from http://alexking.org/blog/2003/06/02/inserting-at-the-cursor-using-javascript
function insertAtCursor(myField, myValue) {
    var startPos, endPos;

    // IE
    if (document.selection){
        myField.focus();
        sel = document.selection.createRange();
        sel.text = myValue;
    }
    // Others
    else if (myField.selectionStart || myField.selectionStart === 0) {
        startPos = myField.selectionStart;
        endPos = myField.selectionEnd;
        myField.value = myField.value.substring(0, startPos) + myValue + myField.value.substring(endPos, myField.value.length);
    }
    else {
        myField.value += myValue;
    }
    //insertAtCursor(document.formName.fieldName, 'this value');
}


// From http://stackoverflow.com/questions/499126/jquery-set-cursor-position-in-text-area
function setSelectionRange(input, selectionStart, selectionEnd) {
  if (input.setSelectionRange) {
    input.focus();
    input.setSelectionRange(selectionStart, selectionEnd);
  }
  else if (input.createTextRange) {
    var range = input.createTextRange();
    range.collapse(true);
    range.moveEnd('character', selectionEnd);
    range.moveStart('character', selectionStart);
    range.select();
  }
}
function setCaretToPos (input, pos) {
  setSelectionRange(input, pos, pos);
}

function moveCaretToEnd(input){
    setCaretToPos(editorElem[0], input.value.length);
}

function autoHeight(elem){
    elem.css("height", "auto");
    elem.height(elem.attr("scrollHeight"));
}

function removeDataAttr(elem){
    jQuery.each(elem[0].attributes, function(i, attr){
        if (attr.specified && attr.nodeName.indexOf("data-") === 0){
            elem.removeAttr(attr.nodeName);
        }
    });
    return elem;
}


function getData(callback){
    var url = debug ? "tmp_data.json" : "/fluffs/";
    jQuery.getJSON(url, callback);
}

function updatePreview(){
    previewElem.html(
        toHtml(editorVal)
    );
}
//updatePreview = throttle(updatePreview, previewUpdateThrottle, true);

function saveToCache(){
    cache.set("content", editorVal);
}
saveToCache = throttle(saveToCache, cacheSaveThrottle, true);

function getCachedContent(){
    return cache.get("content");
}

function updateAll(){
    var oldVal = editorVal;
    
    editorVal = editorElem.val();
    if (oldVal !== editorVal){
        autoHeight(editorElem);
        updatePreview();
        saveToCache();
    }
}
updateAll = throttle(updateAll, updateThrottle, true);

function init(data){
    var fluff = data.fluff.sort(sortByTimestamp);
        
    editorVal = getCachedContent();

    jQuery.each(fluff, function(i, lint){
        jQuery.each(lint.assets, function(i, asset){
            var content;
            try {
                content = tim(asset.media_type, asset);
            }
            catch(e){
                content = "";
            }
            lint.assets[i].content = content;
        }); 
    });

    fluffElem
        .html(
            tim("fluff", data)
        )
        .delegate("[draggable]", "dragstart",function(e){
            var dataTransfer = e.originalEvent.dataTransfer,
                elem = jQuery(this),
                cloneElem = elem.clone(),
                type = elem.attr("data-type"),
                dropContent = elem.attr("data-drop"),
                dropElem = cloneElem.children(),
                dropNode = dropElem[0],
                width, height, reduction;

            if (!type){
                return false;
            }
               
            if (!dropContent){
                switch(type){
                    case "image":                
                    width = dropNode.width;
                    height = dropNode.height;
                    
                    if (width > maxImageWidth){
                        reduction = maxImageWidth / width;
                        width = maxImageWidth;
                        height = Math.round(height * reduction);
                    }
                    if (height > maxImageHeight){
                        reduction = maxImageHeight / height;
                        height = maxImageHeight;
                        width = Math.round(width * reduction);
                    }
                
                    dropElem
                        .attr("width", width)
                        .attr("height", height);
                    
                    dropContent = jQuery.trim(cloneElem.html());
                    break;
                    
                    case "twitter":
                    dropContent = jQuery.trim(cloneElem.html());
                    break;
                }
            }
            
            dataTransfer.effectAllowed = "copy";
            dataTransfer.setData("text/html", dropContent);
        });
            
    editorElem
        .bind({
            cut: updateAll,
            paste: updateAll,
            keyup: updateAll,
            change: updateAll
        })
        
        // DnD modified from http://html5rocks.com/tutorials/dnd/basics/
        .bind("dragover", function(e){
            var dataTransfer = e.originalEvent.dataTransfer;
        
            if (e.preventDefault) {
                e.preventDefault(); // Necessary. Allows us to drop.
            }
            dataTransfer.dropEffect = "copy";
            return false;
        })
        .bind("drop", function(e){
            var dataTransfer = e.originalEvent.dataTransfer;
            
            if (e.stopPropagation) {
                e.stopPropagation(); // stops the browser from redirecting.
            }

            insertAtCursor(editorElem[0], dataTransfer.getData('text/html'));
            
            updateAll();
            editorElem.focus();

            return false;
        });
    
    function updateTweets(content){
        tweetsElem.html(content);
    }
        
    twitterUserElem.change(function(){
        var username = twitterUserElem.val();
        if (username){
            faveTweets(username, function(tweets){
                updateTweets(tim("tweets", {tweets:tweets}));
            });
        }
        else {
            updateTweets("");
        }
    });
        
        // TODO: restore from localStorage, and if populated, then run this
        // moveCaretToEnd(editorElem[0]); editorElem.blur()
        
        
        /* TODO: add settings:
            * inputs for max width, height, img as markdown/html
            * store in localStorage
        */
    if (editorVal){
        editorElem.val(editorVal);
        moveCaretToEnd(editorElem[0]);
        autoHeight(editorElem);
        updatePreview();
    }
}

getData(init);
