/**
 *
 **/
Ext._define('estagio.comissao.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getComissaoGrid: function() {
        if(!this._conceitogrid) {
            this._conceitogrid = Ext._create('estagio.comissao.ComissaoAvaliadoraGrid', {
                region: 'center',
                title: 'Comissão',
                minHeight: 200,
            });

            this._conceitogrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.observe(data.get('pk'));
                },
                rowdeselect: function() {
                    this.observe(null);
                }
            });

        }

        return this._conceitogrid;
    },

    getIntegranteGrid: function() {
        if(!this._configuracaogrid) {
            this._configuracaogrid = Ext._create('estagio.comissao.IntegrantesComissaoGrid', {
                region: 'south',
                height: 400,
                title: 'Integrantes',
                disabled: true,
                gridAutoLoad: false,
            });

        }

        return this._configuracaogrid;
    },

    observe: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._param = value;

            if(!prevent)
                this.observeComissao();
        }

        return this._param;
    },

     observeComissao: function(){

        var value = this.observe();

        if(value) {
            this.getIntegranteGrid().enable();
            this.getIntegranteGrid().servidor = value;
            this.getIntegranteGrid().setFilterProperty('comissao_id', value);
            this.getIntegranteGrid().setParam('comissao_id', value);
        }
        else {
            this.getIntegranteGrid().getStore().removeAll();
            this.getIntegranteGrid().disable();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Comissão Avaliadora'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getComissaoGrid(),
                    this.getIntegranteGrid(),
                ]
            }
        );

        estagio.comissao.Manage.superclass.constructor.call(this, cfg);
    }
});
