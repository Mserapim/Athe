/**
 *
 **/

Ext._define('rh.gfp.socialsecurity.SocialSecurityManage', {
	extend: 'toolkit.widget.TabPanel',

	previdencia: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._previdencia = value;

			if(dispatch) this.observePrevidencia();
		}
		else
			return this._previdencia;
	},

	observePrevidencia: function() {
		if(this.previdencia()){
			this.getFaixa().enable();
			this.getFaixa().setParam('previdencia', this.previdencia());
			this.getFaixa().setFilterProperty('previdencia_id', this.previdencia(), 100);
		}
		else{
			this.getFaixa().disable();
			this.getFaixa().getStore().removeAll();
			this.getFaixa().setFilterProperty('previdencia_id', 0, 100, false);
		}
	},

	getGrid: function() {
		if(!this._previdenciaGrid){
			this._previdenciaGrid = Ext._create('rh.gfp.socialsecurity.SocialSecurityGrid', {
				region: 'center',
				minHeight: 300,
			});

			this._previdenciaGrid.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.previdencia(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.previdencia(null);
				},
			});
		}
		return this._previdenciaGrid;
	},

	getFaixa: function() {
	    if(!this._faixaGrid)
	        this._faixaGrid = Ext._create('rh.gfp.socialsecurity.SocialSecurityRangeGrid', {
	        	id: 'rh.gfp.socialsecurity.SocialSecurityRangeGrid',
	        	region: 'south',
				minHeight: 300,
				height: 400,
				split: true,
				gridAutoLoad: false
	        });
	
	    return this._faixaGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Previdência Social/Privada'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getGrid(),
					this.getFaixa()
				]
			}
		);

		rh.gfp.socialsecurity.SocialSecurityManage.superclass.constructor.call(this, cfg);
		this.observePrevidencia();
	}
});
