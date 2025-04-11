Ext.ns('toolkit.questionario');

Ext.apply(toolkit.questionario, {

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
    }

});