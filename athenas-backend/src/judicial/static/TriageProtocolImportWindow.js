Ext._define('judicial.TriageProtocolImportWindow', {
    extend: 'judicial.ProtocolImportWindow',

    importProtocol: function() {
        var selected = this.getInboxPanel().getSelectionModel().getSelected();
        var validate = this.validate_submit(selected);
        var rest = Ext._create('judicial.OutCourtLawsuitRestful');
        var mask;

        if(validate.valid) {
            mask = new Ext.LoadMask(this.getEl(), {msg: 'importando protocolo ...'});
            mask.show();
            rest.importFromProtocol(
                {
                    protocol: selected.get('protocol'),
                    location: this.params.location,
                    type_lawsuit: this.typeLawsuitBox().getValue()
                },
                {
                    scope: this,
                    fn: function(instance) {
                        core.invokeCallback(this.success || {fn: Ext.emptyFn}, instance);
                        this.close();
                    }
                },
                {
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Importando de protocolo',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {
                    fn: function() { mask.hide(); }
                }
            );
        }
        else
            Ext.Msg.show({
                title: 'Importando de protocolo',
                msg: validate.msg,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    validate_submit: function(selected){
        var type_lawsuit = this.typeLawsuitBox().getValue();

        if (!type_lawsuit)
            return {'valid': false, 'msg': "Selecione o tipo de procedimento."}

        if(selected && !selected.get('with_workflow'))
            return {'valid': true, 'msg': ''}
        else
            return {'valid': false, 'msg': 'Primeiro selecione o protocolo que deseja importar.'}

    },

    typeLawsuitBox: function() {
        if(!this._typeLawsuit)
            this._typeLawsuit = Ext._create('standard.fields.ChoiceField', {
                name: 'type_lawsuit',
                choiceId: 'judicial.IMPORT_TYPE_LAWSUIT',
            });

        return this._typeLawsuit;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                'Importar como:',
                this.typeLawsuitBox()
            ].concat(judicial.TriageProtocolImportWindow.superclass.getButtons.call(this, cfg));

        return this._buttons;
    }

});
