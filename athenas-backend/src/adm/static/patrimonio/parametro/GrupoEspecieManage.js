/**
 *
 **/

Ext._define('adm.patrimonio.parametro.GrupoEspecieManage', {
     extend: 'toolkit.widget.TabPanel',

    getGrupoContabilGrid: function() {
     if(!this._grupoContabilGrid) {
         this._grupoContabilGrid = Ext._create('adm.patrimonio.parametro.GrupoContabilGrid', {
            region: 'west',
            minWidth:250,
            width: Ext.getBody().getBox().width * 0.20,
            split: true,
            // columnAction: false
        });

        this._grupoContabilGrid.getSelectionModel().on({
            scope: this,
            rowselect: function(grid, index, record) {
                this.setGrupoContabil(record.get('pk'));
            }
        });

        this._grupoContabilGrid.getSelectionModel().on({
            scope: this,
            rowdeselect: function() {
                this.setGrupoContabil(undefined);
            }
        });
     }

     return this._grupoContabilGrid;
    },

    observe_grupoespecie: function() {
        if(this.grupoContabilId) {
            this.getGrupoEspecieGrid().enable();
            this.getGrupoEspecieGrid().setFilterProperty('grupo_contabil', this.grupoContabilId);
            this.getGrupoEspecieGrid().setParam('grupo_contabil', this.grupoContabilId);
            // this.getGrupoEspecieGrid().getStore().load({});
        }
        else {
            this.getGrupoEspecieGrid().disable();
        }
    },

    setGrupoContabil: function(pk) {
        this.grupoContabilId = pk;
        this.observe_grupoespecie();
    },

    getGrupoContabil: function() {
        return this.grupoContabilId;
    },

    getGrupoEspecieGrid: function() {
        if(!this._grupoEspecieGrid) {
            this._grupoEspecieGrid = Ext._create('adm.patrimonio.parametro.GrupoEspecieGrid', {
                region: 'center',
                minWidth:200,
                split: true,
                gridAutoLoad: false,
                disabled: true,
            });

            this._grupoEspecieGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    this.setGrupoEspecie(record.get('pk'));
                }
            });

            this._grupoEspecieGrid.getSelectionModel().on({
                scope: this,
                rowdeselect: function() {
                    this.setGrupoEspecie(undefined);
                }
            });
        }

        return this._grupoEspecieGrid;
    },

    observe: function() {
        if(this.grupoEspecieId) {
            this.getEspecieGrid().enable();
            this.getEspecieGrid().setFilterProperty('grupo', this.grupoEspecieId);
            this.getEspecieGrid().setParam('grupo', this.grupoEspecieId);
            // this.getEspecieGrid().getStore().load({});
        }
        else {
            this.getEspecieGrid().disable();
        }
    },

    setGrupoEspecie: function(pk) {
        this.grupoEspecieId = pk;
        this.observe();
    },

    getGrupoEspecie: function() {
        return this.grupoEspecieId;
    },

    getEspecieGrid: function() {
     if(!this._especieGrid)
         this._especieGrid = Ext._create('adm.patrimonio.parametro.EspecieGrid', {
            gridAutoLoad: false,
            region: 'east',
            minWidth: 300,
            width: Ext.getBody().getBox().width * 0.4,
            split: true,
            disabled: true
        });

     return this._especieGrid;
    },

    constructor: function(cfg) {
     cfg = cfg ? cfg : {};

     Ext.applyIf(
         cfg,
         {
            title: 'Gestor de Grupo Especie'
         }
     );

     Ext.apply(
         cfg,
         {
            layout: 'border',
            items: [
                this.getGrupoContabilGrid(),
                this.getGrupoEspecieGrid(),
                this.getEspecieGrid()
            ]
         }
     );

     adm.patrimonio.parametro.GrupoEspecieManage.superclass.constructor.call(this, cfg);
    }
 });
