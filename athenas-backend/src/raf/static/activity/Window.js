Ext._define('raf.activity.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.activity.Restful',

    prepareFields: function(cfg) {
        var fields = [
            {
                xtype: 'displayfield',
                fieldLabel: 'Promotoria',
                name: 'workerlocation_unicode',
            },
            {
                xtype: 'hidden',
                name: 'workerlocation',
            },
            {
                xtype: 'displayfield',
                fieldLabel: 'Questionário',
                name: 'quiz_unicode',
            },
            {
                xtype: 'displayfield',
                fieldLabel: 'Item',
                name: 'item_unicode',
            },
            {
                xtype: 'hidden',
                name: 'item',
            },
            {
                xtype: 'displayfield',
                fieldLabel: 'SubItem',
                name: 'subitem_unicode',
            },
            {
                xtype: 'hidden',
                name: 'subitem',
            },
        ];

        if(cfg.params.manual_amount)
            fields.push(
                {
                    xtype: "numberfield",
                    width: 100,
                    allowBlank: false,
                    fieldLabel: "Quantidade",
                    name: "amount_submitted",
                }
            );
        else
            fields.push(
                {
                    xtype: "displayfield",
                    fieldLabel: "Qtd. Aferida",
                    name: "amount_athenas",
                },
                {
                    xtype: "displayfield",
                    fieldLabel: "Qtd. à submeter",
                    name: "amount_submitted",
                }
            );

        return fields;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.prepareFields(cfg)
                ]
            });

        return this._formPanel;
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});


        Ext.applyIf(cfg,
            {
                width: 600,
                title: 'Atividade',
            }
        );
        raf.activity.Window.superclass.constructor.call(this, cfg);
        this.getFormPanel().getForm().setValues(cfg.values);
        console.log(this.getFormPanel().getForm());
    }
});
