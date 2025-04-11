Ext._define('raf.adjustment.AdjustmentEmployeeWindow', {
    extend: 'raf.adjustment.BaseWindow',

    rest: 'raf.adjustment.AdjustmentEmployeeRestful',

    save: function(close) {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Criando atividade...'});

        if(values.activity == 0) {
            mask.show();
            Ext.Ajax.request({
                url: core.callAction('RAFActivityAdjustmentEmployee', 'get_or_create_activity'),
                scope: this,
                params: values,
                callback: function() {
                    mask.hide();
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        values.activity = rst.activity;
                        this.getFormPanel().getForm().setValues(values);
                        raf.adjustment.AdjustmentEmployeeWindow.superclass.save.call(this, close);
                        // core.invokeCallback((this.callback || {}).success);
                    }

                },
                failure: function() {}
            });
        } else
            raf.adjustment.AdjustmentEmployeeWindow.superclass.save.call(this, close);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        raf.adjustment.AdjustmentEmployeeWindow.superclass.constructor.call(this, cfg);
    }

});
