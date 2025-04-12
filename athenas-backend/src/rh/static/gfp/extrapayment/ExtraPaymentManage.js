/**
 *
 **/

Ext._define('rh.gfp.extrapayment.ExtraPaymentManage', {
	extend: 'toolkit.widget.TabPanel',

	extraPayment: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._extraPayment = value;

			if(dispatch) this.observeExtraPayment();
		}
		else
			return this._extraPayment;
	},

	observeExtraPayment: function() {
		if(this.extraPayment()){
			this.getPeriodGrid().enable();
			this.getPeriodGrid().setParam('extra_payment', this.extraPayment());
			this.getPeriodGrid().setFilterProperty('extra_payment_id', this.extraPayment(), 100);
		}
		else{
			this.getPeriodGrid().disable();
			this.getPeriodGrid().getStore().removeAll();
			this.getPeriodGrid().setFilterProperty('extra_payment_id', 0, 100, false);
		}
	},

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.extrapayment.ExtraPaymentGrid', {
				region: 'west',
 				width: 600,
 	            minWidth: 600,
				split: true,
			});
			
			this._grid.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.extraPayment(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.extraPayment(null);
				},
			});

			this._grid.getStore().on({
				scope: this,
				beforeload: function(gd, opts){
					var rec = this._grid.getSelectionModel().getSelected();
					this._grid.getSelectionModel().clearSelections();
					this.extraPayment(null);
					if(rec){
						this._grid.getSelectionModel().selectRecords([rec]);
					}

				}
			})

		return this._grid;
	},

	getPeriodGrid: function() {
		if(!this._periodGrid)
			this._periodGrid = Ext._create('rh.gfp.extrapayment.ExtraPaymentPeriodGrid', {
				region: 'center',
	        	// region: 'south',
				// minHeight: 300,
				// height: 400,
				layout: 'fit',
				values: {extra_payment: this.extraPayment(),},
				params: {end_validity: null},
				disabled: true,
				gridAutoLoad: false				
			});

		return this._periodGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Verbas Extras / Auxílios'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					this.getGrid(),
					this.getPeriodGrid(),
				]
			}
		);

		rh.gfp.extrapayment.ExtraPaymentManage.superclass.constructor.call(this, cfg);
	}
});
