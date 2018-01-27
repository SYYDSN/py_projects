(function (window) {
    var svgSprite = '<svg><symbol id="icon-yujing_mian" viewBox="0 0 1024 1024"><path d="M268.233114 895.522883h-64.822354V595.269495c0-170.387645 138.128941-308.514539 308.516585-308.514539 170.388668 0 308.515562 138.126894 308.515563 308.514539v300.254412h-71.250764M534.23849 411.06517L382.048299 661.728116h121.757065l-30.442336 188.010002L625.554242 599.056752H503.804341l30.434149-187.991582zM767.645424 135.724171c14.276145 8.283664 19.169595 26.600845 10.927887 40.933271l-54.720275 95.143941-51.693336-29.964452 54.719252-95.143941c8.241708-14.32731 26.494421-19.23918 40.766472-10.968819zM511.838318 65.24805c17.886369 0 32.389688 13.501502 32.389687 30.159903v107.818611h-64.778352V95.407953c0-16.658402 14.499226-30.159904 32.388665-30.159903zM256.20415 135.724171c14.276145-8.270361 32.530904-3.358491 40.772612 10.967796l54.719252 95.14394-51.698452 29.964452-54.719253-95.14394c-8.238638-14.331403-3.350304-32.648584 10.925841-40.932248zM69.00256 323.661517c8.242731-14.332427 26.495444-19.24532 40.771589-10.974958l94.776574 54.941309-29.845749 51.891858-94.776573-54.925961c-14.276145-8.27957-19.167548-26.598798-10.925841-40.932248zM954.848037 323.661517c8.242731 14.332427 3.354398 32.652677-10.921747 40.933272l-94.776574 54.92596-29.845748-51.891857 94.774527-54.94131c14.274098-8.270361 32.530904-3.357468 40.769542 10.973935z"  ></path><path d="M97.634668 895.522883h828.585355c17.945721 0 32.494065 14.546298 32.494065 32.492019s-14.548344 32.495088-32.494065 32.495088H97.634668c-17.945721 0-32.494065-14.549368-32.494065-32.495088s14.548344-32.492018 32.494065-32.492019z"  ></path></symbol></svg>';
    var script = function () {
        var scripts = document.getElementsByTagName("script");
        return scripts[scripts.length - 1]
    }();
    var shouldInjectCss = script.getAttribute("data-injectcss");
    var ready = function (fn) {
        if (document.addEventListener) {
            if (~["complete", "loaded", "interactive"].indexOf(document.readyState)) {
                setTimeout(fn, 0)
            } else {
                var loadFn = function () {
                    document.removeEventListener("DOMContentLoaded", loadFn, false);
                    fn()
                };
                document.addEventListener("DOMContentLoaded", loadFn, false)
            }
        } else if (document.attachEvent) {
            IEContentLoaded(window, fn)
        }

        function IEContentLoaded(w, fn) {
            var d = w.document, done = false, init = function () {
                if (!done) {
                    done = true;
                    fn()
                }
            };
            var polling = function () {
                try {
                    d.documentElement.doScroll("left")
                } catch (e) {
                    setTimeout(polling, 50);
                    return
                }
                init()
            };
            polling();
            d.onreadystatechange = function () {
                if (d.readyState == "complete") {
                    d.onreadystatechange = null;
                    init()
                }
            }
        }
    };
    var before = function (el, target) {
        target.parentNode.insertBefore(el, target)
    };
    var prepend = function (el, target) {
        if (target.firstChild) {
            before(el, target.firstChild)
        } else {
            target.appendChild(el)
        }
    };

    function appendSvg() {
        var div, svg;
        div = document.createElement("div");
        div.innerHTML = svgSprite;
        svgSprite = null;
        svg = div.getElementsByTagName("svg")[0];
        if (svg) {
            svg.setAttribute("aria-hidden", "true");
            svg.style.position = "absolute";
            svg.style.width = 0;
            svg.style.height = 0;
            svg.style.overflow = "hidden";
            prepend(svg, document.body)
        }
    }

    if (shouldInjectCss && !window.__iconfont__svg__cssinject__) {
        window.__iconfont__svg__cssinject__ = true;
        try {
            document.write("<style>.svgfont {display: inline-block;width: 1em;height: 1em;fill: currentColor;vertical-align: -0.1em;font-size:16px;}</style>")
        } catch (e) {
            console && console.log(e)
        }
    }
    ready(appendSvg)
})(window)