function splashFadeIn(el) {
    var control = 0;

    var clock = setInterval(
        function() {
            control++;

            try { el.style.opacity = (control / 10); }
            catch(e) { control = 10; }

            if(control == 10) {
                clearInterval(clock);
                clock = false;
            }
        },
        100
    );
}

splashFadeIn(document.getElementById('nowLoading'));

/** check debuger **/
if(window.console == undefined) {
    var f_void = function() { };
    window.console = {
        log       : f_void,
        info      : f_void,
        warn      : f_void,
        debug     : f_void,
        error     : f_void,
        assert    : f_void,
        dir       : f_void,
        dirxml    : f_void,
        trace     : f_void,
        group     : f_void,
        groupEnd  : f_void,
        time      : f_void,
        timeEnd   : f_void,
        profile   : f_void,
        profileEnd: f_void,
        count     : f_void
    };
}
/** end check debuger **/
Ext.onReady(function() {
    setTimeout(
        function() {
            if(location.protocol != "https:" && force_secure) {
                setTimeout(function() {
                        location.href = "https://" + location.hostname + location.pathname;
                    },
                    2000
                );
            }

            Ext.BLANK_IMAGE_URL = '/' + CONTEXT + '/static/js/ext/resources/images/default/s.gif';
            if(Ext.chart != undefined)
                Ext.chart.Chart.CHART_URL = '/' + CONTEXT + '/static/js/ext/resources/charts.swf';

            toolkit.Application.start();
            Ext.getBody().dom.removeChild(document.getElementById('nowLoading'));
        },
        250
    );

});

/** change logomarca **/
var interval;
var i = 1;
interval = setInterval(function() {
    if(!!document.getElementById('header') == true){
        el = document.getElementById('header');
        el.firstChild.setAttribute('style', "background: url(/athenas/static/images/"+header_h1_img_name+") no-repeat;");
        clearInterval(interval);
    }
    i++; if(i == 10){ clearInterval(interval); }
}, 100);