Ext._define('corregedoria.reportbuilder.BaseWindow', {
    extend: 'engine.mq.ReportWindow',

    _listOutputFormat: [
	    {
	        title: 'Arquivo PDF',
	        type: 'PDF',
	        iconCls: 'icon-ged icon-ged-application-pdf'
	    },
	],

    _controller: '',

    prepareValues: function(values) {
        return values;
    },

    engine: function(values, filename, reportName) {
        engine.mq.Report.request(
            {
                reportBuilder: this._controller,
                report: this._report,
                params: Ext.apply(
                    values,
                    {
                        outfile: filename,
                        report_name: reportName,
                        format: this.outputFormat()
                    }
                ),
                el: this.getEl(),
                waitMessage: this._waitMessage,
            },
            this.outputFormat()
        );
    },

    generateReport: function(preventClose) {
        preventClose = core.nullValue(preventClose, false);

        if(!this.getFormPanel().getForm().isValid())
            return;

        var values = this.getFormPanel().getForm().getValues();
        var reportName = this.reportName(values);
        var filename = this.filename(values);

        values = this.prepareValues(values);

        this.engine(values, filename, reportName);

        if(preventClose)
            this.getFormPanel().getForm().reset();
        else
            this.close();
    },

});
