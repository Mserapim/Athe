Ext._define('rh.pvf.absence.privateinterest.Window', {
    extend: 'rh.pvf.absence.absence.Window',

    rest: 'rh.pvf.absence.privateinterest.Restful',

    getGeneralInfoFieldSet: function (cfg) {
        return []
    },

    save:function(cfg){
        var params = this.getFormPanel().getForm().getValues()
        substitutes_data = this.setStoreSubstitute(this.getSubstituteStore())
        params['substitutes'] = JSON.stringify(substitutes_data)
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});  
        mask.show();
        rest.doRequest(
            rest.getRoute('save', false, 'POST', {
                scope: this,
                params,
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.ownerGrid.getStore().reload()
                        this.destroy();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atenção',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        ); 

    }

});

