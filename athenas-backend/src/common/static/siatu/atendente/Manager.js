/**
 *
 **/
Ext._define('common.siatu.atendente.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getAtendenteGrid: function() {
        if(!this._atendenteGrid){
            this._atendenteGrid = Ext._create('common.siatu.atendente.Grid', {
                flex: 0.4
            });

            this._atendenteGrid.getKeywordField().setWidth(130);

            this._atendenteGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    this.getChamadoGrid().setFilterProperty('atendentes', record.get('pk'), 0, true);
                    this.getChamadoGrid().setTitle('Chamados do atendente ' + record.get('nome'));
                }
            });
         }

        return this._atendenteGrid;
     },

    getChamadoGrid: function() {
        if(!this._chamadoGrid){
            this._chamadoGrid = Ext._create('common.siatu.chamado.Grid', {
                flex: 0.6,
                title: 'Chamados do atendente',
                manager: 'adm',
                gridAutoLoad: false,
                concluido: this.concluido,
                filterStatus: this.filterStatus,
                status_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getChamadoGrid().getStore().reload();
                        }
                    }
                },
                update_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getChamadoGrid().getStore().reload();
                        }
                    }
                }
            });

            this._chamadoGrid.getKeywordField().setWidth(130);
            this._chamadoGrid.setFilterProperty('status_atual__status__in', this.filterStatus, 1000, false);
        }

         return this._chamadoGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this.concluido = cfg.concluido;

        if (Ext.util.Cookies.get('siatu-chamado-filterStatus') != null)
            this.filterStatus = Ext.decode(Ext.util.Cookies.get('siatu-chamado-filterStatus'));
        else
            this.filterStatus = [1, 2, 3, 5, 6, 7, 8, 10];

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Atendentes'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'hbox',
                layoutConfig:{
                    align: 'stretch'
                },
                items: [
                    this.getAtendenteGrid(),
                    this.getChamadoGrid()
                ]
            }


        );

        common.siatu.atendente.Manager.superclass.constructor.call(this, cfg);
    }
});

