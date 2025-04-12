/**
 *
 **/
Ext._define('common.siatu.chamado.avaliacao.WindowIntervencao', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.avaliacao.Restful',

    width: 430,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                labelAlign: 'top',
                items: [
                    {
                        xtype: 'textarea',
                        name: 'sugestao',
                        fieldLabel: 'Comentário',
                        width: 400
                    }

                ]
            });

        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        var sugestao = form.getValues().sugestao;
        var rest = Ext._create('common.siatu.chamado.avaliacao.Restful', {});
        // var mask = new Ext.LoadMask(this.getEl(), {msg: 'Aplicando dados...'});
        // mask.show();
        rest.doRequest(
            rest.getRoute('apply_intervencao', false, 'POST', {
                params: {
                    pk: this.IdChamado,
                    sugestao: sugestao
                },
                scope: this,
                callback: function() {
                    // mask.hide();
                    // mask = null;
                },
                success: function(xhr) {
                    // mask.hide();
                    // mask = null;
                    this.destroy()
                    // this.getGrid().getStore().reload();
                    // this.callback.call(this.scope ? this.scope : window);
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Erro',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Não consegui aplicar as informações'
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
                title: 'Intervenção',
                disableSaveAndNew: true,
            }
        );
        this.IdChamado = cfg.IdChamado;
        common.siatu.chamado.avaliacao.WindowIntervencao.superclass.constructor.call(this, cfg);
    }
});
