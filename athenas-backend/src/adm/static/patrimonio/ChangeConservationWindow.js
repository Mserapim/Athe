
Ext._define('adm.patrimonio.ChangeConservationWindow', {
    extend: 'Ext.Window',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Conservação',
                        name: 'conservacao',
                        hiddenName: 'conservacao',
                        choiceId: 'patrimonio.CONSERVATION',
                        width: 215
                    }
                ]
            });

        return this._formPanel;
    },

    applyChange: function() {
        var rest = Ext._create('adm.patrimonio.PatrimonioRestful');
        var conservation = this.getFormPanel().getForm().getValues().conservacao;
        var defaultCallback = {fn: function() {}};
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Aplicando modificações...'});

        mask.show();
        rest.changeConsevation(
            this.pkset,
            conservation,
            {
                scope: this,
                fn: function() {
                    core.invokeCallback((this.success || defaultCallback));
                    this.close();
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Alterando estado de conservação',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                    mask = null;
                }
            }
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true,
                title: 'Mudar estado de conservação',
                width: 350
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                items: [
                    this.getFormPanel()
                ],
                buttons: [
                    {
                        text: 'Aplicar',
                        scope: this,
                        handler: this.applyChange
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: function() { this.close(); }
                    }
                ]
            }
        );

        // this.callParent([]);
        adm.patrimonio.ChangeConservationWindow.superclass.constructor.call(this, cfg);
    }
});
