
Ext._define('web.cms.file.ApplyMonthWindow', {
    extend: 'Ext.Window',

    getFormPanel: function(cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'combobox',
                        fieldLabel: 'Mês',
                        name: 'ref_month',
                        mode: 'local',
                        store: Ext._create('Ext.data.ArrayStore', {
                            idIndex: 0,
                            fields: [{ name: 'id', type: 'int' }, { name: 'title', type: 'string'}],
                            data: [
                                [1, 'Janeiro'],
                                [2, 'Fevereiro'],
                                [3, 'Março'],
                                [4, 'Abril'],
                                [5, 'Maio'],
                                [6, 'Junho'],
                                [7, 'Julho'],
                                [8, 'Agosto'],
                                [9, 'Setembro'],
                                [10, 'Outubro'],
                                [11, 'Novembro'],
                                [12, 'Dezembro'],
                            ],
                        }),
                        valueField: 'id',
                        displayField: 'title',
                        editable: false,
                        triggerAction: 'all'
                    }
                ]
            });
        }

        return this._formPanel;
    },

    save: function() {
        var rest = Ext._create('web.cms.file.Restful');
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'aplicando...' });

        mask.show();
        rest.applyMonth(
            {
                pkset: this.pkset,
                ref_month: this.getFormPanel().getForm().getValues().ref_month
            },
            {
                scope: this,
                fn: function() {
                    core.invokeCallback((this.callback || {}).success || { fn: Ext.emptyFn });
                    this.close();
                }
            },
            {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Aplicando valor de Mês',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function () { mask.hide() }
            }
        );
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            title: 'Aplicando valor de mês',
            modal: true,
            closable: true,
            width: 360,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Applicar',
                    scope: this,
                    handler: function() { this.save() }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ]
        });

        web.cms.file.ApplyMonthWindow.superclass.constructor.call(this, cfg);
    }
})
