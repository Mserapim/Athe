/**
 *
 **/
Ext._define('judicial.tac.WindowSignature', {
    extend: 'core.RestfulWindow',

    'rest': 'judicial.tac.ManagementTACRestful',

    width: 400,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                labelAlign: 'top',
                items: [
                    {
                        xtype: 'datefield',
                        name: 'date_signature',
                        fieldLabel: 'Data da Assintura da TAC',
                        width: 360
                    }

                ]
            });

        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        var date_signature = form.getValues().date_signature;
        var rest = Ext._create('judicial.tac.ManagementTACRestful', {});
        var mask = new Ext.LoadMask(this.getEl(), {'msg': 'Aplicando dados...'});
        mask.show();
        rest.doRequest(
            rest.getRoute('apply_signature', false, 'POST', {
                params: {
                    pk: this.idTac,
                    date_signature: date_signature
                },
                scope: this,
                'callback': function() {
                    mask.hide();
                    mask = null;
                },
                success: function(xhr) {
                    this.destroy();
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        'title': 'Erro',
                        'icon': Ext.Msg.ERROR,
                        'buttons': Ext.Msg.OK,
                        'msg': 'Não consegui aplicar as informações'
                    });
                }
            })
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(
            cfg,
            {
                title: 'Assinatura',
                disableSaveAndNew: true,
            }
        );
        this.idTac = cfg.idTac
        judicial.tac.WindowSignature.superclass.constructor.call(this, cfg);
    }
});
