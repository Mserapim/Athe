/**
 *
 **/
Ext._define('cif.controlinformationmember.Manage', {
    extend: 'cif.Manage',

    getInformationMember: function() {
        if(!this._informationmember) {
            this._informationmember = Ext._create('cif.controlinformationmember.ControlMember', {
                title:'Gestor de Informações',
                region: 'center',
            });

            this._informationmember.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, record) {
                    //alterei de record.data.pk para record
                    this.setInformationMember(record);
                },
                rowdeselect: function(sm) {
                    this.setInformationMember(null);
                }
            });

            this._informationmember.getStore().on({
                scope: this,
                load: function() {
                    this.setInformationMember(null);
                }
            });

            this._informationmember.getStore().on({
                scope: this,
                load: function() {
                    var selected = (this._informationmember.getSelectionModel().getSelected());
                    if(selected)
                        this.setInformationMember(selected.get('pk'));
                    else
                        this.setInformationMember(null);
                }
            });
        }

        return this._informationmember;
    },

});
