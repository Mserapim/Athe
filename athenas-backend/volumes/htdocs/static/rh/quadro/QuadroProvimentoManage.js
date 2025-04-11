/**
 *
 **/

Ext._define('rh.quadro.QuadroProvimentoManage', {
	extend: 'toolkit.widget.TabPanel',

	getQuadroGrid: function() {
		if(!this._quadroGrid)
			this._quadroGrid = Ext._create('rh.quadro.Grid', {
				region: 'center'
			});

		this._quadroGrid.getSelectionModel().on({
            scope: this,
            rowselect: function(sm, index, data) {
                this.observe(data.get('pk'));
            },
            rowdeselect: function() {
                this.observe(null);
            }
        });

		return this._quadroGrid;
	},

	getProvimentoGrid: function() {
        if(!this._provimentoGrid) {
            this._provimentoGrid = Ext._create('rh.movimentacao.possession.provision.Grid', {
                region: 'south',
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                height: 400,
                disabled: true,
                gridAutoLoad: false,
            });
            toolbar = this._provimentoGrid.getToolbar();
            toolbar.remove(toolbar.getComponent(6));
            toolbar.remove(toolbar.getComponent(0));
            toolbar.remove(toolbar.getComponent(0));
            toolbar.remove(toolbar.getComponent(0));
            toolbar.remove(toolbar.getComponent(0));
            toolbar.remove(toolbar.getComponent(0));

        }

        return this._provimentoGrid;
    },

    observe: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._param = value;

            if(!prevent)
                this.observeQuadro();
        }

        return this._param;
    },

    observeQuadro: function(){

        var value = this.observe();

        if(value) {
            this.getProvimentoGrid().enable();
            this.getProvimentoGrid().quadro = value;
            this.getProvimentoGrid().setFilterProperty('quadro', value);
            this.getProvimentoGrid().setParam('quadro', value);
        }
        else {
            this.getProvimentoGrid().getStore().removeAll();
            this.getProvimentoGrid().disable();
        }
    },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Quadros e Provimentos'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					this.getQuadroGrid(),
					this.getProvimentoGrid()
				]
			}
		);

		rh.quadro.QuadroProvimentoManage.superclass.constructor.call(this, cfg);
	}
});
