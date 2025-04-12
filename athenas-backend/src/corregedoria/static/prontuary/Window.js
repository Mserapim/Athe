Ext._define('corregedoria.protuary.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.protuary.Restful',
    width: 810,

    getFormPanel: function() {
      if(!this._formPanel) {
        this._formPanel =
            Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                ],
            });
        }
        return this._formPanel;
    },
});
