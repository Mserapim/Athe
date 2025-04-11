Ext._define('engine.mq.OutputFormatReportMixin', {

	_defaultOutputFormat: 'PDF',

    _reportButtonText: 'Gerar relatório',

	_listOutputFormat: [
	    {
	        title: 'Arquivo PDF',
	        type: 'PDF',
	        iconCls: 'icon-ged icon-ged-application-pdf'
	    },
	    {
	        title: 'Arquivo CSV',
	        type: 'CSV',
	        iconCls: 'icon-ged icon-ged-text-plain',
	    },
        {
	        title: 'Arquivo XLS',
	        type: 'XLS',
	        iconCls: 'icon-ged icon-ged-application-vnd-ms-excel'
	    },
        {
	        title: 'Arquivo ODT',
	        type: 'ODT',
	        iconCls: 'icon-ged icon-ged-application-msword'
	    },
	],

    generateReport: function(preventClose) {
        throw 'Method generateReport not implemented';
    },

	getListOutputFormat: function() {
	    return this._listOutputFormat;
	},

	outputFormat: function() {
        return this._defaultOutputFormat;
    },

	getAllFormatType: function() {
        if(!this._allFormatType) {
            var me = this;
                        
            this._allFormatType = this.getListOutputFormat().map(
                function(item) {
                    return {
                        text: item.title,
                        iconCls: item.iconCls, 
                        handler: function() {
                            me.formatSelected(item.type, item.iconCls);
                        }
                    }  
                }
            );
        }
        
        return this._allFormatType;
    },

    formatSelected: function(format, icon) {
        this._defaultOutputFormat = format.toUpperCase();
        this.getRunReportButton().setIconClass(icon);
        this.generateReport(true);
    },  

    getRunReportButton: function(cfg) {  
        if(!this._runReportSplitBtn) {
            var me = this;
            this._runReportSplitBtn = Ext._create('Ext.Toolbar.SplitButton', {
                text: this._reportButtonText,
                scope: this,
                handler: function() { 
                	me.generateReport(true);
                },
                iconCls: 'icon-ged icon-ged-application-pdf',
                menu : {
                    items: this.getAllFormatType()
                }
            });
        }

        return this._runReportSplitBtn;
    },

});