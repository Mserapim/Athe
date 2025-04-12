/**
 *
 **/
Ext._define('rh.falta.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getServidorGrid: function() {
        if(!this._servidor) {
            this._servidor = Ext._create('rh.falta.employee.Grid', {
                region: 'center',
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                height: 200,
                split: true,
            });

            this._servidor.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.observe(data.get('servidor_pk'));
                },
                rowdeselect: function() {
                    this.observe(null);
                }
            });

            this._servidor.getStore().on({
				scope: this,
				beforeload: function(st, options){
					rec = this._servidor.getSelectionModel().getSelected();
					this._servidor._lastEvent = rec? rec.data.pk: null;
				},
				load: function(st, records, options){
					if(!records.length)
						this.observe(null);
				}
			});
        }

        return this._servidor;
    },

    getFaltaGrid: function() {
        if(!this._subfaltaGrid) {
            this._subfaltaGrid = Ext._create('rh.falta.FaltaGrid', {
                region: 'south',
                height: 400,
                disabled: true,
                gridAutoLoad: false,
                split: true,
            });
        }

        return this._subfaltaGrid;
    },

    observe: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._param = value;

            if(!prevent)
                this.observeFalta();
        }

        return this._param;
    },

    observeFalta: function(){

        var value = this.observe();
        var opcao = ['processado', 'aguardando_analise', 'removido'];
        var filtros_aplicar = []

        if(value) {
            this.getFaltaGrid().enable();
            this.getFaltaGrid().servidor = value;
            this.getFaltaGrid().setFilterProperty('servidor', value, 1001, false);
            this.getFaltaGrid()._toolbar.items.items.forEach(function(item){
				if(item.text == 'Filtrar Situação'){
					item.menu.items.items.forEach(function(itemSituacao){
						if(itemSituacao.id == 'todos' && itemSituacao.checked == true){
                            filtros_aplicar.push(1,2,3);
                        }else if(
                            (itemSituacao.id != 'todos' && opcao.includes(itemSituacao.id) && itemSituacao.checked == true)
                        ){
                            filtros_aplicar.push(itemSituacao.value);
                        }
					});
				}
			});
            this.getFaltaGrid().setFilterProperty('situacao__in', filtros_aplicar, 1002, true);
            this.getFaltaGrid().setParam('servidor', value);
        }
        else {
            this.getFaltaGrid().getStore().removeAll();
            this.getFaltaGrid().disable();
        }
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Faltas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getServidorGrid(),
                    this.getFaltaGrid()
                ]
            }
        );

        rh.falta.Manage.superclass.constructor.call(this, cfg);
    }
});
