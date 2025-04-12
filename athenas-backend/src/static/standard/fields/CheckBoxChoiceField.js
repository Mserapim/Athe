/**
 *
 **/
Ext._define('standard.fields.CheckBoxChoiceField', {
    extend: 'Ext.Panel',

    xtype: 'checkboxchoicefield',

    choiceStore: function(cfg) {
        if(!this._choicestore) {
            var restful = 'standard.ChoiceActiveRestful';
            this._choicestore = Ext._create(restful).getStore(false);
            this._choicestore.baseParams.limit = 125;
            this._choicestore.baseParams.filter = Ext.encode([
                {
                    property: 'cache_path',
                    value: cfg.checkconfig.choiceId
                }
            ]);
        }
        this._choicestore.on('load', function() {
            panel = Ext.getCmp(cfg.checkconfig.name);
            ckg = {
                xtype: cfg.singleSelection == true ? 'radiogroup' : 'checkboxgroup',
                id: 'ck_' + cfg.checkconfig.name,
                columns: cfg.checkconfig.columns || 1,
                fieldLabel: cfg.checkconfig.fieldLabel || cfg.checkconfig.name,
                hideLabel: cfg.checkconfig.hideLabel || false,
                vertical: cfg.checkconfig.vertical || false,
                items: [
                    {boxLabel: 'ZERO', name: 'zero'},
                ],
            };
            this.each(
                function(record,idx){
                    ckg.items[idx] = {
                        boxLabel: record.data.label,
                        name: cfg.singleSelection == true ? cfg.checkconfig.name : (cfg.checkconfig.name+''+record.data.value),
                        inputValue: record.data.value,
                        checked: cfg.checkconfig.items_db && (cfg.checkconfig.items_db.indexOf(''+record.data.value) >= 0) ? true : false,
                    };
                }
            );
            panel.add(ckg);
            panel.doLayout();
        });
        return this._choicestore;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        if(!cfg.checkconfig.choiceId)
            throw 'É necessário que se especifique ou o choideId ou o choicePath';
        if(!cfg.checkconfig.name)
            throw 'É necessário que se especifique o name';
        Ext.applyIf(
            cfg,
            {
                id: cfg.checkconfig.name,
            }
        );
        Ext.apply(
            cfg,
            {
                autoHeight:true,
                layout: 'form',
            }
        );
        standard.fields.CheckBoxChoiceField.superclass.constructor.call(this, cfg);
        this.choiceStore(cfg).load();
    }
});
Ext.reg('checkboxchoicefield', standard.fields.CheckBoxChoiceField);
