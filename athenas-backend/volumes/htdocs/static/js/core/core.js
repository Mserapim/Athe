/**
 *
 **/
Ext.ns('core');

Ext.applyIf(core, {

    reloadStyleSheet: function() {
        var i, a, s;

        a = document.getElementsByTagName('link');

        for(i = 0; i < a.length; i++) {
            s = a[i];
            if(s.rel.toLowerCase().indexOf('stylesheet') >= 0 && s.href) {
                var h = s.href.replace(/(&|%5C?)forceReload=\d+/, '');
                s.href = h + (h.indexOf('?') >=0 ? '&' : '?') + 'forceReload=' + (new Date().valueOf());
            }
        }
    },

    voidCallback: {
        fn: function() {}
    },

    'invokeCallback': function(callback, arg) {
        if(callback) {
            var scope = (callback.scope ? callback.scope : window);
            try {
                return (callback.fn || Ext.emptyFn).call(scope, arg);
            }
            catch(e) {
                console.error(e);
            }
        }
    },

    rendererIconGrid: function(value) {
        var tpl = new Ext.XTemplate('<div class="tk-grid-icon-cell {iconCls}" ext:qtip="{title}" <tpl if="width">ext:qwidth="{width}</tpl>"></div>');
        var out = '';

        Ext.each(value, function(item) {
            if(item)
                out += tpl.apply({
                    'iconCls': item.iconCls,
                    'title': item.title,
                    'width': (item.width ? item.width : false)
                });
        });

        return out;
    },

    'nullValue': function(a, b) {
        return a != undefined ? a : b;
    },

    'getClassFromName': function(name) {
        var cls = undefined;

        try {
            cls = eval(name);
        }
        catch(e) {
            cls = undefined;
        }
        finally {
            return cls;
        }
    },

    'callAction': function(controller, action, args) {
        var url = '';

        url += '/' + global.Context;
        url += '/' + controller;
        url += '/' + (action ? action : 'index');

        Ext.each(args, function(part) {
            url += '/' + part;
        });

        if(!/^.*\/$/.test(url))
            url += '/';

        return url;
    }
});
