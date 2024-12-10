"use strict";
var KTUsersAddAuthApp = function () {
    const t = document.getElementById("kt_modal_add_auth_app"),
        e = new bootstrap.Modal(t);
    return {
        init: function () {
            t.querySelector('[data-kt-users-modal-action="close"]').addEventListener("click", (t => {
                t.preventDefault(), Swal.fire({
                    text: "Are you sure you would like to close?",
                    icon: "warning",
                    showCancelButton: !0,
                    buttonsStyling: !1,
                    confirmButtonText: "Yes, close it!",
                    cancelButtonText: "No, return",
                    customClass: {
                        confirmButton: "btn btn-primary",
                        cancelButton: "btn btn-active-light"
                    }
                }).then((function (t) {
                    t.value && e.hide()
                }))
            })), (() => {
                const e = t.querySelector('[ data-kt-add-auth-action="qr-code"]'),
                    n = t.querySelector('[ data-kt-add-auth-action="text-code"]'),
                    o = t.querySelector('[ data-kt-add-auth-action="qr-code-button"]'),
                    a = t.querySelector('[ data-kt-add-auth-action="text-code-button"]'),
                    c = t.querySelector('[ data-kt-add-auth-action="qr-code-label"]'),
                    d = t.querySelector('[ data-kt-add-auth-action="text-code-label"]'),
                    l = () => {
                        e.classList.toggle("d-none"), o.classList.toggle("d-none"), c.classList.toggle("d-none"), n.classList.toggle("d-none"), a.classList.toggle("d-none"), d.classList.toggle("d-none")
                    };
                a.addEventListener("click", (t => {
                    t.preventDefault(), l()
                })), o.addEventListener("click", (t => {
                    t.preventDefault(), l()
                }))
            })()
        }
    }
}();
KTUtil.onDOMContentLoaded((function () {
    KTUsersAddAuthApp.init()
}));