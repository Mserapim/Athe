/**
 *
 **/
Ext._define('rh.teletrabalho.gestor_relatorio_semestral.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGestorGrid: function(cfg) {
        if(!this._gestor) {
            this._gestor = Ext._create('rh.teletrabalho.gestor_relatorio_semestral.gestor.Grid', {
                region: 'center',
                columnAction: true,
                allowCreate: false,
                allowUpdate: false,
                height: 200,
                split: true,
                lista_periodos: cfg.lista_periodos,
            });

            this._gestor.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.observe(data.get('pk'), sm.grid.params );
                },
                rowdeselect: function() {
                    this.observe(null);
                }
            });
        }

        return this._gestor;
    },
    getServidorGrid: function() {
        if(!this._servidor) {
            this._servidor = Ext._create('rh.teletrabalho.gestor_relatorio_semestral.servidor.Grid', {
                region: 'south',
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                height: 400,
                disabled: true,
                gridAutoLoad: false,
                split: true,
            });

        }

        return this._servidor;
    },



    observe: function(value, params, prevent) {
        prevent = core.nullValue(prevent, false);


        if(value !== undefined && params !== undefined) {
            this._param = new Map();
            this._param.set('pk', value);
            this._param.set('data_inicio', params.data_inicio);
            this._param.set('data_fim', params.data_fim);


            if(!prevent)
                this.observeServidor();
        }

        return this._param;
    },

    observeServidor: function(){

        var value = this.observe();

        if(value) {
            this.getServidorGrid().enable();
            this.getServidorGrid().aprovador = value.get('pk');
            this.getServidorGrid().setFilterProperty('aprovador', value.get('pk'), 1001, true);
            this.getServidorGrid().setFilterProperty('data_inicio__lte', value.get('data_fim'), 1002, false);
            this.getServidorGrid().setFilterProperty('data_fim__gte', value.get('data_inicio'), 1003, true);


            this.getServidorGrid().setParam('aprovador', value.get('pk'));
        }
        else {
            this.getServidorGrid().getStore().removeAll();
            this.getServidorGrid().disable();
        }
    },







    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Relatorio Semestral'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGestorGrid(cfg),
                    this.getServidorGrid(),
                ]
            }
        );

        rh.teletrabalho.gestor_relatorio_semestral.Manage.superclass.constructor.call(this, cfg);
    }
});
