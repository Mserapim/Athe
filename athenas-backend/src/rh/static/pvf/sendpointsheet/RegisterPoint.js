/*****************************************************************************
*                                                                            *
*                            FOLHA PONTO                          *
*                                                                            *
*****************************************************************************/
Ext._define('rh.pvf.sendpointsheet.RegisterPoint', {
	extend: 'toolkit.widget.TabPanel',

    BACKGROUND_COLOR: '#005a7d',
    CARD_HEIGHT: 200,
    CARD_WIDTH: 550,
    REGION: 'center',
    GAP: 50,
    LEFT_PADDING: 450,
    BOTTOM_PADDING: 100,

    REPORT_CLASS: null,

    PDF_FUNCTION: null,
    XLS_FUNCTION: null,
    CSV_FUNCTION: null,

    _getDefaults: function () {
        return {
            flex: 1,
            height: this.CARD_HEIGHT,
            width: this.CARD_WIDTH,
            baseCls: 'x-river-panel',
            align: this.REGION,
        };
    },

	getMain: function(cfg){
		if(!this._panel)
		this._panel = new Ext.Panel({
            region: 'south',
		    height: 900,
            bodyStyle: {
                'background-color': `${this.BACKGROUND_COLOR}`,
            },           
            layout: {
                type: 'hbox',
                padding: `${this.GAP} ${this.GAP} ${this.BOTTOM_PADDING} ${this.LEFT_PADDING}`,
            },
            defaults: this._getDefaults(),
		    autoEl: {tag: 'center'},
		    items: [
                {
	        		xtype: 'fieldset',
	        		name: 'fieldServidor',
                    title: 'Registro de Ponto',
                    bwrapStyle: [
                        'border-radius: 0px 0 8px 8px;',
                        'background-color: #005a7c;',
                        'font-size: 14px;',
                        'font-weight: bold;',
                        'cursor: default;',
                        'user-select: none;',
                    ].join(''),
	        		align: 'center',
                    items:Ext._create('rh.registerpoint.RegisterPointForm')
                }
            ]
            
            
	    });

		return this._panel;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Registrar Ponto'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'fit',
				items:[ 
					this.getMain(cfg),
				]
			}
		);

		rh.pvf.sendpointsheet.RegisterPoint.superclass.constructor.call(this, cfg);
	}
});