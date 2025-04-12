/**
 *
 **/
Ext._define('stats.Colector', {
    extend: 'Object',

    statics: {
        cookieName: function() {
            return 'mpto.Telemetry';
        },

        validAt: function() {
            return new Date(new Date().getTime() + (7 * 24 * 60 * 60 * 1000))
        },

        register: function(seed) {
            Ext.util.Cookies.set(stats.Colector.cookieName(), seed, stats.Colector.validAt());
        },

        _scanBroweserInfo: function() {
            var sentence = /(Safari|Edge|Firefox|Opera|Chrome)\/(.*)/;
            var data = navigator.userAgent.split(' ').filter(function(str) { return sentence.test(str) });

            if (data.length > 0) {
                var info = data[0].split('/');
                return {
                    browser: info[0],
                    version: info[1].split('.')[0]
                };
            } else {
                return {
                    browser: 'other',
                    version: 'other'
                };
            }
        },

        scan: function() {
            var rst = {};

            var b = stats.Colector._scanBroweserInfo();

            rst = {
                screenWidth: screen.width,
                screenHeight: screen.height,
                screenColorDepth: screen.colorDepth,
                bodyWidth: Ext.getBody().getBox().width,
                bodyHeight: Ext.getBody().getBox().height,
                language: navigator.language,
                platform: navigator.platform,
                vendor: navigator.vendor,
                browser: b.browser,
                version: b.version,
            }

            return rst;
        },

        send: function() {
            var stid = Ext.util.Cookies.get(stats.Colector.cookieName());

            if(!stid)
                Ext.Ajax.request({
                    url: core.callAction('Stats', 'persist'),
                    params: {
                        stats: Ext.encode(stats.Colector.scan())
                    },
                    success: function(request) {
                        var rst = Ext.decode(request.responseText);
                        console.info('Stats registred!')
                        stats.Colector.register(rst.seed);
                    },
                    failure: function() {
                        console.error('Stats not registred!')
                    }
                });
            else
                console.info('Stats already registred!');
        }
    }
});
